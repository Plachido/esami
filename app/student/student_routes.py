# student/student_routes.py
from flask import Blueprint, session, redirect, url_for, render_template, request, flash, jsonify
from database import get_db_connection
import random  # Make sure to import random for shuffling
from datetime import datetime, timedelta  # Import datetime for submission time
student_bp = Blueprint('student', __name__)
# student/student_routes.py

from flask import Blueprint, session, redirect, url_for, render_template, request, flash, jsonify
from database import get_db_connection
import random

student_bp = Blueprint('student', __name__)

@student_bp.route('/enter_test_code', methods=['GET', 'POST'])
def enter_test_code():
    if 'username' not in session or session['user_type'] != 'alunno':
        return redirect(url_for('auth.index'))
    
    if request.method == 'POST':
        data = request.get_json()
        session_code = data.get('testCode')
        
        if not session_code:
            return jsonify({"message": "Test code is required."}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Check if the test code is valid, active, and not expired
            cursor.execute("""
                SELECT test_id, data_generazione, exam_duration, stopped 
                FROM codice 
                WHERE id = %s
                AND active = 1
                AND (data_generazione + INTERVAL exam_duration MINUTE) > NOW() 
                AND stopped = 0;
            """, (session_code,))
            code_entry = cursor.fetchone()
            if code_entry:
                test_code = code_entry[0]
                duration_in_minutes = code_entry[2]
                start_time = code_entry[1]
                end_time = start_time + timedelta(minutes=duration_in_minutes)
                
                # Calculate remaining time in seconds
                remaining_time = int((end_time - datetime.now()).total_seconds())
                
                session['remaining_time'] = remaining_time  # Pass to frontend
                session['test_code'] = test_code
                session['session_code'] = session_code
                session.modified = True

                user = session['username']
                cursor.execute("SELECT submission_date FROM test_alunno WHERE alunno_username = %s AND codice_id = %s", (user, session_code))
                submission = cursor.fetchone()

                if submission:
                    flash('Test already submitted. You cannot retake this test.')
                    return redirect(url_for('auth.index'))

                # Insert a new record into test_alunno
                start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute("""
                    INSERT INTO test_alunno (alunno_username, codice_id, voto, start_time)
                    VALUES (%s, %s, NULL, %s)
                """, (user, session_code, start_time))
                conn.commit()

                # Check if there are responses with alunno_username, codice_id
                cursor.execute("SELECT * FROM risposta WHERE alunno_username = %s AND codice_id = %s", (user, session_code))
                responses = cursor.fetchall()

                # Fetch only active questions for the test
                cursor.execute("""
                    SELECT domanda.id AS domanda_id, domanda.testo AS domanda_text, 
                           opzione.id AS opzione_id, opzione.testo AS opzione_text, 
                           opzione.vero AS is_correct, 0 AS ordine
                    FROM domanda
                    JOIN opzione ON opzione.domanda_id = domanda.id
                    WHERE domanda.test_id = %s
                    AND domanda.active = 1;
                """, (test_code,))
                questions = cursor.fetchall()
                structured_questions = restructure_questions(questions)

                if responses:
                    # If there are existing responses, load them into the session
                    session['answers'] = [None] * len(structured_questions)
                    for response in responses:
                        question_id = response[2]
                        option_id = response[3]
                        order = response[4]
                        cursor.execute("SELECT testo FROM opzione WHERE id = %s", (option_id,))
                        option_text = cursor.fetchone()[0]
                        question_index = next((i for i, q in enumerate(structured_questions) if q['id'] == question_id), None)
                        if question_index is not None:
                            session['answers'][question_index] = option_text
                else:
                    # If no responses exist, initialize responses for each question
                    random.shuffle(questions)
                    structured_questions = restructure_questions(questions)
                    for order, question in enumerate(structured_questions):
                        cursor.execute("""
                            INSERT INTO risposta (alunno_username, codice_id, domanda_id, opzione_id, ordine)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (user, session_code, question['id'], None, order))
                    conn.commit()
                    session['answers'] = [None] * len(structured_questions)

                session['questions'] = structured_questions
                session.modified = True
                return redirect(url_for('student.exam'))
            else:
                return jsonify({"message": "Invalid, inactive, or expired test code."}), 400
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"message": "An error occurred."}), 500
        finally:
            cursor.close()
            conn.close()

    return render_template('enter_test_code.html')




def restructure_questions(data):
    # Initialize an empty dictionary to hold question data
    question_dict = {}
    
    # Iterate through each entry in the data
    for q_id, question_text, opt_id, option_text, is_correct, order in data:
        # If the question ID is not already in the dictionary, initialize it
        if q_id not in question_dict:
            question_dict[q_id] = {
                "id": q_id,
                "question": question_text,
                "options": [],
                "answer": None,
                "value": 1,  # Set the value based on the order + 1
                "order": order  # Set the order based on the input data
            }
        
        # Append the option text to the question's options list
        question_dict[q_id]["options"].append(option_text)
        
        # If this option is correct, set it as the answer
        if is_correct == 1:
            question_dict[q_id]["answer"] = option_text
            

    # Convert the dictionary to a list of question dictionaries
    questions = list(question_dict.values())
    
    # Sort questions by 'value' key if order matters
    questions.sort(key=lambda x: x["order"])
    #drop the order key
    for question in questions: del question['order']
    
    return questions

@student_bp.route('/submit_answer', methods=['POST'])
def submit_answer():
    if 'username' not in session or 'questions' not in session:
        return redirect(url_for('auth.index'))

    answer = request.form.get('answer')
    question_index = int(request.form['question_index'])
    
    # Store the answer in session and database
    temp = session['answers']
    temp[question_index] = answer
    session['answers'] = temp
    session.modified = True

    conn = get_db_connection()
    cursor = conn.cursor()

    question = session['questions'][question_index]
    domanda_id = question['id']
    code_id = session['test_code']  # Use the test code from session
    session_code = session['session_code']
    user = session['username']
    
    # Create the SQL query string with placeholders
    query = """
    UPDATE risposta
    SET opzione_id = (
        SELECT id
        FROM opzione
        WHERE testo = %s
        AND domanda_id = %s
    )
    WHERE alunno_username = %s
    AND codice_id = %s
    AND domanda_id = %s;
    """

    cursor.execute(query, (answer, domanda_id, user, session_code, domanda_id))
    conn.commit()
    cursor.close()
    conn.close()

    # Determine next question index
    next_index = request.form.get('next_index')
    prev_index = request.form.get('prev_index')

    if next_index is not None:  # If next question is requested
        return redirect(url_for('student.exam', q=int(next_index)))
    elif prev_index is not None:  # If previous question is requested
        return redirect(url_for('student.exam', q=int(prev_index)))
    else:
        return redirect(url_for('student.exam', q=question_index))  # Default to the current question


@student_bp.route('/exam')
def exam():
    if 'username' not in session or 'questions' not in session:
        return redirect(url_for('auth.index'))
    print(session['answers'])
    question_index = int(request.args.get('q', 0))
    if question_index < len(session['questions']):
        question = session['questions'][question_index]
        return render_template('exam.html', question=question, index=question_index, total=len(session['questions']), selected_answer=session['answers'][question_index])
    else:
        return redirect(url_for('student.exam_results'))

# The rest of your routes, including submit_answer and exam_results, remain the same.


@student_bp.route('/review')
def review():
    if 'username' not in session:
        return redirect(url_for('index'))
    
    questions = session.get('questions')
    answers = session.get('answers')
    
    return render_template('review.html', questions=questions, answers=answers)


@student_bp.route('/exam_results')
def exam_results():
    if 'username' not in session or 'questions' not in session:
        return redirect(url_for('auth.index'))

    questions = session['questions']
    answers = session['answers']
    results = []

    # Evaluate the answers
    for question, user_answer in zip(questions, answers):
        correct_options = [option['vero'] for option in question['options'] if option['vero'] == 1]
        results.append({
            'question': question['testo'],
            'user_answer': user_answer,
            'correct': user_answer in correct_options
        })

    return render_template('exam_results.html', results=results)

@student_bp.route('/check_active_status')
def check_active_status():
    session_code = session.get('session_code')
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT active FROM codice WHERE id = %s", (session_code,))
    active = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    return jsonify({"active": active == 1})


@student_bp.route('/submit_exam', methods=['POST'])
def submit_exam():
    if 'username' not in session or 'questions' not in session:
        return redirect(url_for('auth.index'))

    conn = get_db_connection()
    cursor = conn.cursor()

    user = session['username']
    session_code = session['session_code']
    submission_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute("UPDATE test_alunno SET submission_date = %s WHERE alunno_username = %s AND codice_id = %s",
                   (submission_time, user, session_code))
    conn.commit()
    conn.close()

    # Clear session variables for security
    session.pop('questions', None)
    session.pop('answers', None)
    session.pop('remaining_time', None)
    
    return jsonify({"message": "Exam submitted successfully"})

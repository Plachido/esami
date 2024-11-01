# professor/professor_routes.py
from flask import Blueprint, session, redirect, url_for, render_template, request, flash
from database import get_db_connection
from utils import get_active_exam_session
import datetime


professor_bp = Blueprint('professor', __name__)

@professor_bp.route('/professor/professor_tests')
def professor_tests():
    if 'username' not in session or session['user_type'] != 'professore':
        return redirect(url_for('auth.index'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    username = session['username']
    cursor.execute("SELECT * FROM test WHERE professore_username = %s", (username,))
    tests = cursor.fetchall()

    active_codes = get_active_exam_session(cursor)
    test_session_map = {}
    current_time = datetime.datetime.now()

    for code in active_codes:
        test_id = code['test_id']
        start_time = code['data_generazione']
        exam_duration = code['exam_duration']
        expiry_time = start_time + datetime.timedelta(minutes=exam_duration)
        remaining_time = (expiry_time - current_time).total_seconds()

        if test_id not in test_session_map:
            test_session_map[test_id] = []

        test_session_map[test_id].append({
            'code_id': code['id'],
            'remaining_time': remaining_time
        })

    conn.close()
    return render_template('professor_tests.html', tests=tests, test_session_map=test_session_map)


@professor_bp.route('professor/create_test', methods=['GET', 'POST'])
def create_test():
    if 'username' not in session or session['user_type'] != 'professore':
        return redirect(url_for('auth.index'))

    if request.method == 'POST':
        test_name = request.form['test_name']
        username = session['username']

        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("INSERT INTO test (nome, professore_username) VALUES (%s, %s)", (test_name, username))
            test_id = cursor.lastrowid  # Get the id of the inserted test

            # Process questions
            questions = []
            for key in request.form:
                if key.startswith('questions['):
                    index = int(key.split('[')[1].replace(']', ''))-1  # Extract the question index
                    if 'text' in key and 'options' not in key:
                        questions.append({'text': request.form[key], 'options': []})
                    elif 'options' in key:
                        option_index = int(key.split('[')[3].replace(']', ''))-1  # Extract the option index
                        if 'text' in key:
                            questions[int(index)]['options'].append({'text': request.form[key], 'correct': 0})  # Default correct value
                        elif 'correct' in key:
                            questions[index]['options'][option_index]['correct'] = 1 if request.form[key] == '1' else 0

            # Insert questions and their options into the database
            for question in questions:
                question_text = question['text']
                cursor.execute("INSERT INTO domanda (test_id, testo) VALUES (%s, %s)", (test_id, question_text))
                question_id = cursor.lastrowid  # Get the id of the inserted question

                # Insert options
                for option in question['options']:
                    option_text = option['text']
                    is_correct = option.get('correct', 0)  # Default to 0 if not set
                    cursor.execute("INSERT INTO opzione (testo, vero, domanda_id) VALUES (%s, %s, %s)", 
                                   (option_text, is_correct, question_id))

            conn.commit()
            flash('Test created successfully with questions and options!')
        except Exception as e:
            print(f"Error creating test: {e}")  # Error logging
            flash('An error occurred while creating the test.')
        finally:
            conn.close()

        return redirect(url_for('professor.professor_tests'))

    return render_template('create_test.html')


@professor_bp.route('/add_question/<int:test_id>', methods=['GET', 'POST'])
def add_question(test_id):
    if 'username' not in session or session['user_type'] != 'professore':
        return redirect(url_for('auth.index'))

    if request.method == 'POST':
        question_text = request.form['question_text']
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert the question into the database
        cursor.execute("INSERT INTO domanda (test_id, testo) VALUES (%s, %s)", (test_id, question_text))
        question_id = cursor.lastrowid  # Get the id of the inserted question

        # Add options to the question
        options = request.form.getlist('option')
        correct_options = request.form.getlist('correct_option')

        for option_text in options:
            if option_text:  # Only add if the option text is not empty
                is_correct = '1' if option_text in correct_options else '0'
                cursor.execute("INSERT INTO opzione (testo, vero, domanda_id) VALUES (%s, %s, %s)", 
                               (option_text, is_correct, question_id))

        conn.commit()
        flash('Question and options added successfully!')
        return redirect(url_for('professor.professor_tests'))

    return render_template('add_question.html', test_id=test_id)



@professor_bp.route('/start_exam_session/<int:test_id>', methods=['POST'])
def start_exam_session(test_id):
    if 'username' not in session or session['user_type'] != 'professore':
        return redirect(url_for('auth.index'))

    validity_time = int(request.form.get('validity_time', 5))  # Default to 5 minutes
    exam_duration = int(request.form.get('exam_duration', 60))  # Default to 60 minutes from frontend

    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert a new entry in the codice table with data_generazione as the current timestamp
    try:
        cursor.execute(
            "INSERT INTO codice (data_generazione, test_id, validity_time, exam_duration) VALUES (%s, %s, %s, %s)",
            (datetime.datetime.now(), test_id, validity_time, exam_duration)
        )
        conn.commit()
        code_id = cursor.lastrowid  # Get the ID of the newly created code

        flash(f'Exam session started! Code: {code_id}')  # Provide the code to the professor
        #return {'code': code_id, 'validity_time': validity_time, 'exam_duration': exam_duration}
    
    except Exception as e:
        print(f"Error starting exam session: {e}")
        flash('An error occurred while starting the exam session.')

    finally:
        conn.close()

    return redirect(url_for('professor.professor_tests'))

@professor_bp.route('/stop_exam_session/<int:test_id>', methods=['POST'])
def stop_exam_session(test_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM codice WHERE test_id = %s", (test_id,))
        conn.commit()
        flash('Exam session ended successfully!')
    except Exception as e:
        print(f"Error stopping exam session: {e}")
        flash('An error occurred while stopping the exam session.')
    finally:
        conn.close()

    return redirect(url_for('professor.professor_tests'))



import csv
import random
import mysql.connector
from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
import datetime  # Import datetime for handling dates

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Use a strong secret key in production

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="professore"
    )

# Check if the user is a professor or student
def get_user_type(username):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT 'professore' as type FROM professore WHERE username = %s UNION ALL SELECT 'alunno' as type FROM alunno WHERE username = %s", (username, username))
    result = cursor.fetchone()
    
    conn.close()
    return result['type'] if result else None

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Check in both tables for professors and students
    cursor.execute("SELECT username FROM professore WHERE username = %s AND password = %s UNION ALL SELECT username FROM alunno WHERE username = %s AND password = %s", (username, password, username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        session['username'] = username
        user_type = get_user_type(username)
        session['user_type'] = user_type
        if user_type == 'professore':
            return redirect(url_for('professor_tests'))
        else:
            return redirect(url_for('enter_test_code'))
    else:
        flash('Invalid username or password')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('index'))

# Route for student to enter a test code
@app.route('/enter_test_code', methods=['GET', 'POST'])
def enter_test_code():
    # Check if the user is logged in and is an 'alunno'
    if 'username' not in session or session['user_type'] != 'alunno':
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Retrieve the test code from the POST request
        data = request.get_json()
        test_code = data.get('testCode')
        
        if not test_code:
            return "Test code is required", 400

        # Connect to the database and verify the test code
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Check if the test code exists in the database
            cursor.execute("SELECT * FROM codice WHERE id = %s", (test_code,))
            code_entry = cursor.fetchone()
            
            if code_entry:
                # Optionally, set up session variables or additional checks here
                return jsonify({"message": "Test code accepted."})
            else:
                return "Invalid test code.", 400
        except Exception as e:
            print(f"Error checking test code: {e}")
            return "An error occurred.", 500
        finally:
            cursor.close()
            conn.close()

    # If the request method is GET, render the test code entry page
    return render_template('enter_test_code.html')

# Route to load the test based on the entered test code
@app.route('/start_test', methods=['POST'])
def start_test():
    if 'username' not in session or session['user_type'] != 'alunno':
        return redirect(url_for('index'))

    test_code = request.form['test_code']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Retrieve test details based on test code
    cursor.execute("SELECT test_id FROM codice WHERE id = %s", (test_code,))
    code_entry = cursor.fetchone()
    
    if code_entry:
        test_id = code_entry['test_id']
        
        # Load questions for the specific test
        cursor.execute("SELECT * FROM domanda WHERE test_id = %s", (test_id,))
        questions = cursor.fetchall()

        # Store questions in session for the test
        session['questions'] = questions
        session['answers'] = [None] * len(questions)
        session['test_code'] = test_code

        conn.close()
        return redirect(url_for('exam'))
    else:
        flash('Invalid test code')
        conn.close()
        return redirect(url_for('enter_test_code'))


@app.route('/professor_tests')
def professor_tests():
    if 'username' not in session or session['user_type'] != 'professore':
        return redirect(url_for('index'))

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

def get_active_exam_session(cursor):
    cursor.execute("SELECT * FROM codice")
    codes = cursor.fetchall()
    current_time = datetime.datetime.now()
    code_list = []

    for code in codes:
        start_time = code['data_generazione']
        exam_duration = code['exam_duration']
        
        # Calculate expiry time
        expiry_time = start_time + datetime.timedelta(minutes=exam_duration)
        
        if current_time < expiry_time:  # Exam session still active
            code_list.append(code)

    return code_list
@app.route('/create_test', methods=['GET', 'POST'])
def create_test():
    if 'username' not in session or session['user_type'] != 'professore':
        return redirect(url_for('index'))

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

        return redirect(url_for('professor_tests'))

    return render_template('create_test.html')

@app.route('/add_question/<int:test_id>', methods=['GET', 'POST'])
def add_question(test_id):
    if 'username' not in session or session['user_type'] != 'professore':
        return redirect(url_for('index'))

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
        return redirect(url_for('professor_tests'))

    return render_template('add_question.html', test_id=test_id)

@app.route('/stop_exam_session/<int:test_id>', methods=['POST'])
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

    return redirect(url_for('professor_tests'))


from flask import session, request, redirect, url_for, render_template, flash
import datetime
import random

@app.route('/submit_code', methods=['POST'])
def submit_code():
    if 'username' not in session or 'user_type' != 'alunno':
        return redirect(url_for('index'))
    
    user = session['username']
    code_id = request.form.get('code_id')
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if student already submitted this test
    cursor.execute("SELECT submission_date FROM test_alunno WHERE alunno_username = %s AND codice_id = %s", (user, code_id))
    submission = cursor.fetchone()

    if submission:
        flash('Test already submitted. You cannot retake this test.')
        conn.close()
        return redirect(url_for('index'))

    # Retrieve all questions and options for the test if not already answered
    cursor.execute("SELECT domanda.id AS domanda_id, domanda.testo AS domanda_text, opzione.id AS opzione_id, opzione.testo AS opzione_text, opzione.vero AS is_correct "
                   "FROM domanda "
                   "JOIN opzione ON opzione.domanda_id = domanda.id "
                   "WHERE domanda.test_id = (SELECT test_id FROM codice WHERE id = %s)", (code_id,))
    questions = cursor.fetchall()

    # Check if responses exist; if not, initialize them
    cursor.execute("SELECT * FROM risposta WHERE alunno_username = %s AND codice_id = %s", (user, code_id))
    existing_responses = cursor.fetchall()

    if not existing_responses:
        # Randomize questions and insert initial None responses
        question_order = list(range(len(questions)))
        random.shuffle(question_order)

        for order, question in enumerate(question_order):
            domanda_id = questions[question]['domanda_id']
            cursor.execute("INSERT INTO risposta (alunno_username, codice_id, domanda_id, opzione_id, ordine) VALUES (%s, %s, %s, %s, %s)",
                           (user, code_id, domanda_id, None, order))
        conn.commit()

    # Retrieve and sort questions based on their order
    cursor.execute("SELECT domanda.id AS domanda_id, domanda.testo AS domanda_text, opzione.id AS opzione_id, opzione.testo AS opzione_text, opzione.vero AS is_correct, risposta.ordine "
                   "FROM risposta "
                   "JOIN domanda ON domanda.id = risposta.domanda_id "
                   "JOIN opzione ON opzione.domanda_id = domanda.id "
                   "WHERE risposta.alunno_username = %s AND risposta.codice_id = %s "
                   "ORDER BY risposta.ordine", (user, code_id))
    ordered_questions = cursor.fetchall()
    conn.close()

    # Store questions and answers in session
    session['questions'] = ordered_questions
    session['answers'] = [None] * len(ordered_questions)  # Initialize answers

    return redirect(url_for('exam'))

@app.route('/exam')
def exam():
    if 'username' not in session or 'questions' not in session:
        return redirect(url_for('index'))
    
    question_index = int(request.args.get('q', 0))
    question = session['questions'][question_index]
    
    return render_template('exam.html', question=question, index=question_index, total=len(session['questions']), selected_answer=session['answers'][question_index])

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    if 'username' not in session or 'questions' not in session:
        return redirect(url_for('index'))

    answer = request.form.get('answer')
    question_index = int(request.form['question_index'])
    
    # Store the answer in session and database
    session['answers'][question_index] = answer

    conn = get_db_connection()
    cursor = conn.cursor()
    
    question = session['questions'][question_index]
    domanda_id = question['domanda_id']
    code_id = session['code_id']
    user = session['username']
    
    cursor.execute("UPDATE risposta SET opzione_id = %s WHERE alunno_username = %s AND codice_id = %s AND domanda_id = %s",
                   (answer, user, code_id, domanda_id))
    conn.commit()
    conn.close()

    # Redirect to the next question or finish
    if question_index + 1 < len(session['questions']):
        return redirect(url_for('exam') + f'?q={question_index + 1}')
    else:
        # Finish the exam
        return redirect(url_for('exam_results'))

@app.route('/exam_results')
def exam_results():
    if 'username' not in session or 'questions' not in session:
        return redirect(url_for('index'))

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

if __name__ == '__main__':
    app.run(debug=True)

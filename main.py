import csv
import random
import mysql.connector
from flask import Flask, render_template, request, redirect, session, url_for, flash

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
@app.route('/enter_test_code')
def enter_test_code():
    if 'username' not in session or session['user_type'] != 'alunno':
        return redirect(url_for('index'))
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


# Route for professor to view their created tests
@app.route('/professor_tests')
def professor_tests():
    if 'username' not in session or session['user_type'] != 'professore':
        return redirect(url_for('index'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    username = session['username']

    # Retrieve all tests created by this professor
    cursor.execute("SELECT id, nome FROM test WHERE professore_username = %s", (username,))
    tests = cursor.fetchall()
    
    conn.close()
    return render_template('professor_tests.html', tests=tests)

def get_questions(form_result): #ImmutableMultiDict
    questions = []
    while True:
        questio
        

# Route for professor to create a new test
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
            #add dummy question because indexes start from 0
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
                            # Update correct value based on the checkbox
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
        question_text = request.form['question_text']  # Get the question text
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert the question into the database
        cursor.execute("INSERT INTO domanda (test_id, testo) VALUES (%s, %s)", (test_id, question_text))
        question_id = cursor.lastrowid  # Get the id of the inserted question

        # Add options to the question
        options = request.form.getlist('option')  # Change to 'option'
        correct_options = request.form.getlist('correct_option')  # Change to 'correct_option'

        for option_text in options:
            if option_text:  # Only add if the option text is not empty
                is_correct = '1' if option_text in correct_options else '0'  # Check if the option is correct
                cursor.execute("INSERT INTO opzione (testo, vero, domanda_id) VALUES (%s, %s, %s)", 
                               (option_text, is_correct, question_id))

        conn.commit()
        flash('Question and options added successfully!')
        return redirect(url_for('professor_tests'))

    return render_template('add_question.html', test_id=test_id)

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

    question_index = int(request.form['question_index'])
    selected_answer = request.form.get('answer')
    
    session['answers'][question_index] = selected_answer

    next_question = question_index + 1
    if next_question < len(session['questions']):
        return redirect(url_for('exam', q=next_question))
    else:
        return redirect(url_for('review'))

@app.route('/review')
def review():
    if 'username' not in session:
        return redirect(url_for('index'))
    
    questions = session.get('questions')
    answers = session.get('answers')
    
    return render_template('review.html', questions=questions, answers=answers)

@app.route('/submit_exam', methods=['POST'])
def submit_exam():
    if 'username' not in session or 'test_code' not in session:
        return redirect(url_for('index'))

    questions = session.get('questions')
    answers = session.get('answers')
    username = session.get('username')
    test_code = session.get('test_code')

    total_score, max_score = 0, 0
    for i, question in enumerate(questions):
        max_score += question['value'] if 'value' in question else 0
        if answers[i] and answers[i] == question['correct_answer']:  # Assuming there's a way to fetch correct answers
            total_score += question['value']

    percentage = (total_score / max_score) * 100 if max_score > 0 else 0

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE test_alunno SET voto = %s WHERE alunno_username = %s AND codice_id = %s", (percentage, username, test_code))
    conn.commit()
    conn.close()

    flash(f'Exam submitted! Your score is {total_score}/{max_score} ({percentage:.2f}%)')
    session.clear()

    return redirect(url_for('index'))


import datetime  # Import datetime for handling dates

@app.route('/start_exam_session/<int:test_id>', methods=['POST'])
def start_exam_session(test_id):
    if 'username' not in session or session['user_type'] != 'professore':
        return redirect(url_for('index'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert a new entry in the codice table
    try:
        generation_date = datetime.date.today()
        cursor.execute("INSERT INTO codice (data_generazione, test_id) VALUES (%s, %s)", (generation_date, test_id))
        conn.commit()
        code_id = cursor.lastrowid  # Get the ID of the newly created code
        flash(f'Exam session started! Code: {code_id}')  # Provide the code to the professor

    except Exception as e:
        print(f"Error starting exam session: {e}")
        flash('An error occurred while starting the exam session.')
    
    finally:
        conn.close()

    return redirect(url_for('professor_tests'))



if __name__ == '__main__':
    app.run(debug=True)

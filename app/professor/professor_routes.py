# professor/professor_routes.py
from flask import Blueprint, session, redirect, url_for, render_template, request, flash
from database import get_db_connection
from utils import get_active_exam_session
import datetime


professor_bp = Blueprint('professor', __name__)

@professor_bp.route('/create_test/', defaults={'test_id': None}, methods=['GET', 'POST'])
@professor_bp.route('/create_test/<int:test_id>', methods=['GET', 'POST'])
def create_test(test_id):
    if 'username' not in session or session['user_type'] != 'professore':
        return redirect(url_for('auth.index'))

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        test_name = request.form['test_name']
        test_description = request.form.get('test_description', '')  # Get test description
        username = session['username']

        if test_id is None:  # Creating a new test
            cursor.execute("INSERT INTO test (nome, descrizione, professore_username) VALUES (%s, %s, %s)",
                           (test_name, test_description, username))
            test_id = cursor.lastrowid  # Get the id of the inserted test
        else:  # Updating an existing test
            cursor.execute("UPDATE test SET nome = %s, descrizione = %s WHERE id = %s",
                           (test_name, test_description, test_id))

            # Deactivate all old questions for the current test
            cursor.execute("UPDATE domanda SET active = 0 WHERE test_id = %s", (test_id,))

        # Process questions
        questions = []
        for key in request.form:
            if key.startswith('questions['):
                index = int(key.split('[')[1].replace(']', ''))  # Extract the question index
                if 'text' in key and 'options' not in key:
                    questions.append({'text': request.form[key], 'options': []})
                elif 'options' in key:
                    option_index = int(key.split('[')[3].replace(']', ''))  # Extract the option index
                    if 'text' in key:
                        questions[index]['options'].append({'text': request.form[key], 'correct': 0})  # Default correct value
                    elif 'correct' in key:
                        questions[index]['options'][option_index]['correct'] = 1 if request.form[key] == '1' else 0

        # Insert questions and their options into the database
        for question in questions:
            question_text = question['text']
            cursor.execute("INSERT INTO domanda (test_id, testo, active) VALUES (%s, %s, 1)", (test_id, question_text))
            question_id = cursor.lastrowid  # Get the id of the inserted question

            # Insert options
            for option in question['options']:
                option_text = option['text']
                is_correct = option.get('correct', 0)  # Default to 0 if not set
                cursor.execute("INSERT INTO opzione (testo, vero, domanda_id) VALUES (%s, %s, %s)",
                               (option_text, is_correct, question_id))

        conn.commit()
        return redirect(url_for('professor.professor_tests'))

    # If GET, fetch existing test and questions
    if test_id is not None:
        cursor.execute("SELECT nome, descrizione FROM test WHERE id = %s", (test_id,))
        test_data = cursor.fetchone()

        test_name = test_data[0] if test_data else None
        test_description = test_data[1] if test_data else None
        
        cursor.execute("SELECT * FROM domanda WHERE test_id = %s AND active = 1", (test_id,))
        questions = cursor.fetchall()
        
        # Convert tuples to dictionaries for easier manipulation
        questions = [{'id': question[0], 'text': question[1], 'options': []} for question in questions]
        
        # Fetch options for each question
        for question in questions:
            cursor.execute("SELECT * FROM opzione WHERE domanda_id = %s", (question['id'],))
            options = cursor.fetchall()
            question['options'] = [{'id': option[0], 'text': option[1], 'correct': option[2]} for option in options]

        return render_template('create_test.html', test_name=test_name, test_description=test_description, questions=questions, test_id=test_id)

    return render_template('create_test.html', test_name=None, test_description=None, questions=[], test_id=None)



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
        return redirect(url_for('professor.professor_tests'))

    return render_template('add_question.html', test_id=test_id)


@professor_bp.route('/professor_tests')
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


@professor_bp.route('/start_exam_session/<int:test_id>', methods=['POST'])
def start_exam_session(test_id):
    if 'username' not in session or session['user_type'] != 'professore':
        return redirect(url_for('auth.index'))

    exam_duration = int(request.form.get('exam_duration', 60))  # Default to 60 minutes from frontend

    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert a new entry in the codice table with data_generazione as the current timestamp
    try:
        cursor.execute(
            "INSERT INTO codice (data_generazione, test_id, validity_time, exam_duration) VALUES (%s, %s, %s, %s)",
            (datetime.datetime.now(), test_id, exam_duration, exam_duration)
        )
        conn.commit()
        code_id = cursor.lastrowid  # Get the ID of the newly created code

        #return {'code': code_id, 'validity_time': validity_time, 'exam_duration': exam_duration}
    
    except Exception as e:
        print(f"Error starting exam session: {e}")

    finally:
        conn.close()

    return redirect(url_for('professor.professor_tests'))

@professor_bp.route('/stop_exam_session/<int:test_id>', methods=['POST'])
def stop_exam_session(test_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("UPDATE codice SET active = 0 WHERE test_id = %s", (test_id,))
        conn.commit()
    except Exception as e:
        print(f"Error stopping exam session: {e}")
    finally:
        conn.close()

    return redirect(url_for('professor.professor_tests'))


@professor_bp.route('/delete_test/<int:test_id>', methods=['DELETE'])
def delete_test(test_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM test WHERE id = %s", (test_id,))
    conn.commit()
    conn.close()
    return '', 204  # No content, as the test is deleted


@professor_bp.route('/results/<int:test_id>', methods=['GET', 'POST'])
def view_results(test_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'GET':
        print(test_id)
        # Fetch academic years and classes where students submitted the exam
        query = '''
            SELECT DISTINCT anno_scolastico, anno, sezione
            FROM student_grades
            WHERE test_id = %s
        '''
        cursor.execute(query, (test_id,))
        classes = cursor.fetchall()
        unique_academic_years = sorted({cls[0] for cls in classes})
        unique_years = sorted({cls[1] for cls in classes})
        unique_sections = sorted({cls[2] for cls in classes})
        print(unique_academic_years, unique_years, unique_sections)

        # Pass the unique values to the template
        return render_template('results.html', 
                            test_id=test_id, 
                            academic_years=unique_academic_years,
                            years=unique_years,
                            sections=unique_sections)

    elif request.method == 'POST':
        # Fetch selected year and class
        year = request.form.get('anno_scolastico')
        anno = request.form.get('anno')
        sezione = request.form.get('sezione')

        # Query results, including punteggio_massimo and submission_date
        query = '''
            SELECT nome_studente, cognome_studente, risposte_corrette, 
                   risposte_errate, risposte_non_date, punteggio_massimo, submission_date
            FROM student_grades
            WHERE test_id = %s AND anno_scolastico = %s AND anno = %s AND sezione = %s
        '''
        cursor.execute(query, (test_id, year, anno, sezione))
        results = cursor.fetchall()

        # Format results, including the "Risultato" and "Consegna" columns
        formatted_results = [
            {
                'nome_studente': r[0],
                'cognome_studente': r[1],
                'risposte_corrette': r[2],
                'risposte_errate': r[3],
                'risposte_non_date': r[4],
                'risultato': f"{r[2]}/{r[5]}",  # correct/max
                'consegna': r[6].strftime('%Y-%m-%d %H:%M:%S') if r[6] else None  # Only format if submission_date exists
            }
            for r in results if r[6]  # Only include students with a submission_date
        ]

        return render_template('results_table.html', results=formatted_results)

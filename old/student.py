from flask import Blueprint, render_template, session, request

student_bp = Blueprint('student', __name__)


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

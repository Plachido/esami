import csv
from flask import Flask, render_template, request, redirect, session, url_for, flash
import random

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Use a strong secret key in production

# Read users from a text file
def load_users():
    users = {}
    with open('users.txt', 'r') as file:
        for line in file:
            username, password = line.strip().split(',')
            users[username] = password
    return users

# Sample questions and answers (you can later load these from a file)
questions = [
    {"question": "What is 2 + 2?", "options": ["4", "3", "5", "6"], "answer": "4", "value": 1},
    {"question": "Capital of France?", "options": ["Paris", "London", "Berlin", "Rome"], "answer": "Paris", "value": 2},
    {"question": "Who developed Python?", "options": ["Guido van Rossum", "James Gosling", "Linus Torvalds", "Mark Zuckerberg"], "answer": "Guido van Rossum", "value": 3}
]


@app.route('/')
def index():
    return render_template('login.html')
@app.route('/login', methods=['POST'])
def login():
    users = load_users()
    username = request.form['username']
    password = request.form['password']
    
    if username in users and users[username] == password:
        session['username'] = username
        # Shuffle the questions for each user and store in the session
        shuffled_questions = random.sample(questions, len(questions))
        session['questions'] = shuffled_questions
        session['answers'] = [None] * len(questions)  # To store answers
        return redirect(url_for('exam'))
    else:
        flash('Invalid username or password')
        return redirect(url_for('index'))


@app.route('/exam')
def exam():
    if 'username' not in session:
        return redirect(url_for('index'))
    
    question_index = int(request.args.get('q', 0))
    question = session['questions'][question_index]
    shuffled_options = random.sample(question['options'], len(question['options']))
    if 'answers' not in session:
        session['answers'] = [None] * len(questions)
    return render_template('exam.html', question=question, options=shuffled_options, index=question_index, total=len(session['questions']))
@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    if 'username' not in session:
        return redirect(url_for('index'))

    question_index = int(request.form['question_index'])
    selected_answer = request.form.get('answer')

    # Store the answer in the session
    session['answers'][question_index] = selected_answer
    session.modified = True  # Ensure Flask knows the session has been modified

    # Redirect to the next question or back to the exam page
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
    if 'username' not in session:
        return redirect(url_for('index'))

    questions = session.get('questions')
    answers = session.get('answers')  # This is a list, not a dictionary
    username = session.get('username')

    # Initialize score variables
    total_score = 0
    max_score = 0

    # Calculate the total score
    for i, question in enumerate(questions):
        correct_answer = question['answer']
        value = question['value']
        max_score += value  # Update max score with question's value

        # Check if the answer matches the correct one
        print("ANSWER: ", answers[i])
        print("CORRECT: ", correct_answer)
        if answers[i] == correct_answer:  # Use list indexing instead of .get()
            total_score += value  # Add question value if the answer is correct

    # Calculate percentage score
    percentage = (total_score / max_score) * 100

    # Save the result to a CSV file
    with open('grades.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([username, total_score, max_score, percentage])

    flash(f'Exam submitted! Your score is {total_score}/{max_score} ({percentage:.2f}%)')

    # Clear session for next exam
    session.pop('username', None)
    session.pop('questions', None)
    session.pop('answers', None)

    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True)

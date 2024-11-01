# auth/auth_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database import get_db_connection
from utils import get_user_type

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    return render_template('login.html')

@auth_bp.route('/login', methods=['POST'])
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
            return redirect(url_for('professor.professor_tests'))
        else:
            return redirect(url_for('student.enter_test_code'))
    else:
        flash('Invalid username or password')
        return redirect(url_for('auth.index'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('auth.index'))

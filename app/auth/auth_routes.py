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

    # Check in all three tables: professore, alunno, and amministratore
    cursor.execute("""
        SELECT username FROM professore WHERE username = %s AND password = %s
        UNION ALL
        SELECT username FROM alunno WHERE username = %s AND password = %s
        UNION ALL
        SELECT username FROM amministratore WHERE username = %s AND password = %s
    """, (username, password, username, password, username, password))

    user = cursor.fetchone()
    conn.close()

    if user:
        session['username'] = username
        user_type = get_user_type(username)  # Make sure this function can handle 'amministratore'
        session['user_type'] = user_type
        
        if user_type == 'professore':
            return redirect(url_for('professor.professor_tests'))
        elif user_type == 'alunno':
            return redirect(url_for('student.enter_test_code'))
        elif user_type == 'amministratore':
            return redirect(url_for('admin.admin_dashboard'))  # Redirect to admin dashboard
    else:
        flash('Username o password errati')
        return redirect(url_for('auth.index'))


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Utente disconnesso")
    return redirect(url_for('auth.index'))

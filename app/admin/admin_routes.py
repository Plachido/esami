# admin/admin_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
from database import get_db_connection

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_type') != 'amministratore':
            return redirect(url_for('auth.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/admin_dashboard', methods=['GET'])
@admin_required
def admin_dashboard():
    # Example values for anno and sezione
    anno = "2024"
    sezione = "A"
    return render_template('admin_dashboard.html', anno=anno, sezione=sezione)


@admin_bp.route('/manage_students', methods=['GET'])
@admin_required
def manage_students():
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        # Fetch all students
        cursor.execute("SELECT * FROM alunno")
        students = cursor.fetchall()
    return render_template('manage_students.html', students=students)

@admin_bp.route('/add_student', methods=['POST'])
@admin_required
def add_student():
    username = request.form['username']
    nome = request.form['nome']
    cognome = request.form['cognome']
    password = request.form['password']

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO alunno (username, nome, cognome, password) VALUES (%s, %s, %s, %s)", 
            (username, nome, cognome, password)
        )
        conn.commit()
    flash('Student added successfully!')
    return redirect(url_for('admin.manage_students'))

@admin_bp.route('/delete_student/<student_username>', methods=['POST'])
@admin_required
def delete_student(student_username):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM alunno WHERE username = %s", (student_username,))
        conn.commit()
    flash('Student deleted successfully!')
    return redirect(url_for('admin.manage_students'))



@admin_bp.route('/edit_student/<student_username>', methods=['GET', 'POST'])
@admin_required
def edit_student(student_username):
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)

        if request.method == 'POST':
            nome = request.form['nome']
            cognome = request.form['cognome']
            password = request.form['password']
            cursor.execute(
                "UPDATE alunno SET nome = %s, cognome = %s, password = %s WHERE username = %s",
                (nome, cognome, password, student_username)
            )
            conn.commit()
            flash('Student updated successfully!')
            return redirect(url_for('admin.manage_students'))

        cursor.execute("SELECT * FROM alunno WHERE username = %s", (student_username,))
        student = cursor.fetchone()
    return render_template('edit_student.html', student=student)




































































































from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
from database import get_db_connection

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_type') != 'amministratore':
            return redirect(url_for('auth.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/admin_dashboard', methods=['GET'])
@admin_required
def admin_dashboard():
    # Example values for anno and sezione
    anno = "2024"
    sezione = "A"
    return render_template('admin_dashboard.html', anno=anno, sezione=sezione)

@admin_bp.route('/manage_students', methods=['GET'])
@admin_required
def manage_students():
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM alunno")
        students = cursor.fetchall()
    return render_template('manage_students.html', students=students)

@admin_bp.route('/add_student', methods=['POST'])
@admin_required
def add_student():
    username = request.form['username']
    nome = request.form['nome']
    cognome = request.form['cognome']
    password = request.form['password']

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO alunno (username, nome, cognome, password) VALUES (%s, %s, %s, %s)", 
            (username, nome, cognome, password)
        )
        conn.commit()
    flash('Student added successfully!')
    return redirect(url_for('admin.manage_students'))

@admin_bp.route('/delete_student/<student_username>', methods=['POST'])
@admin_required
def delete_student(student_username):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM alunno WHERE username = %s", (student_username,))
        conn.commit()
    flash('Student deleted successfully!')
    return redirect(url_for('admin.manage_students'))

@admin_bp.route('/edit_student/<student_username>', methods=['GET', 'POST'])
@admin_required
def edit_student(student_username):
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)

        if request.method == 'POST':
            nome = request.form['nome']
            cognome = request.form['cognome']
            password = request.form['password']
            cursor.execute(
                "UPDATE alunno SET nome = %s, cognome = %s, password = %s WHERE username = %s",
                (nome, cognome, password, student_username)
            )
            conn.commit()
            flash('Student updated successfully!')
            return redirect(url_for('admin.manage_students'))

        cursor.execute("SELECT * FROM alunno WHERE username = %s", (student_username,))
        student = cursor.fetchone()
    return render_template('edit_student.html', student=student)

@admin_bp.route('/manage_professors', methods=['GET'])
@admin_required
def manage_professors():
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM professore")
        professors = cursor.fetchall()
    return render_template('manage_professors.html', professors=professors)

@admin_bp.route('/add_professor', methods=['POST'])
@admin_required
def add_professor():
    username = request.form['username']
    nome = request.form['nome']
    cognome = request.form['cognome']
    password = request.form['password']

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO professore (username, nome, cognome, password) VALUES (%s, %s, %s, %s)", 
            (username, nome, cognome, password)
        )
        conn.commit()
    flash('Professor added successfully!')
    return redirect(url_for('admin.manage_professors'))

@admin_bp.route('/delete_professor/<professor_username>', methods=['POST'])
@admin_required
def delete_professor(professor_username):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM professore WHERE username = %s", (professor_username,))
        conn.commit()
    flash('Professor deleted successfully!')
    return redirect(url_for('admin.manage_professors'))

@admin_bp.route('/edit_professor/<professor_username>', methods=['GET', 'POST'])
@admin_required
def edit_professor(professor_username):
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)

        if request.method == 'POST':
            nome = request.form['nome']
            cognome = request.form['cognome']
            password = request.form['password']
            cursor.execute(
                "UPDATE professore SET nome = %s, cognome = %s, password = %s WHERE username = %s",
                (nome, cognome, password, professor_username)
            )
            conn.commit()
            flash('Professor updated successfully!')
            return redirect(url_for('admin.manage_professors'))

        cursor.execute("SELECT * FROM professore WHERE username = %s", (professor_username,))
        professor = cursor.fetchone()
    return render_template('edit_professor.html', professor=professor)

















































































@admin_bp.route('/manage_classes', methods=['GET', 'POST'])
@admin_required
def manage_classes():
    if request.method == 'POST':
        selected_academic_year = request.form.get('academic_year')
        return redirect(url_for('admin.class_detail', academic_year=selected_academic_year))
    
    # Fetch academic years
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT anno_scolastico FROM classe")
    academic_years = cursor.fetchall()
    conn.close()

    return render_template('manage_classes.html', academic_years=academic_years)

@admin_bp.route('/class_detail', methods=['GET'])
@admin_required
def class_detail():
    academic_year = request.args.get('academic_year')
    
    # Fetch classes for the selected academic year
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT anno, sezione FROM classe WHERE anno_scolastico = %s", (academic_year,))
    classes = cursor.fetchall()
    conn.close()
    
    return render_template('class_detail.html', classes=classes, academic_year=academic_year)

@admin_bp.route('/students_in_class/<string:academic_year>/<int:anno>/<string:sezione>', methods=['GET', 'POST'])
@admin_required
def students_in_class(academic_year, anno, sezione):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Handle adding a student
    if request.method == 'POST':
        if 'add_student' in request.form:
            student_username = request.form.get('student_username')
            cursor.execute("UPDATE alunno SET anno_scolastico = %s, anno = %s, sezione = %s WHERE username = %s",
                           (academic_year, anno, sezione, student_username))
            conn.commit()
            flash(f'Student {student_username} added to the class!', 'success')

        if 'remove_student' in request.form:
            student_username = request.form.get('remove_student_username')
            cursor.execute("UPDATE alunno SET anno_scolastico = NULL, anno = NULL, sezione = NULL WHERE username = %s",
                           (student_username,))
            conn.commit()
            flash(f'Student {student_username} removed from the class!', 'success')

    # Fetch students in the class
    cursor.execute("SELECT username, nome, cognome FROM alunno WHERE anno_scolastico = %s AND anno = %s AND sezione = %s", 
                   (academic_year, anno, sezione))
    students_in_class = cursor.fetchall()

    # Fetch all students not in the class
    cursor.execute("SELECT username, nome, cognome FROM alunno WHERE (anno_scolastico IS NULL OR (anno <> %s OR sezione <> %s))", 
                   (anno, sezione))
    available_students = cursor.fetchall()

    conn.close()
    return render_template('students_in_class.html', 
                           students=students_in_class, 
                           available_students=available_students, 
                           academic_year=academic_year, 
                           anno=anno, 
                           sezione=sezione)
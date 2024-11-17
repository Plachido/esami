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

        # Fetch available classes (anno and sezione combinations)
        cursor.execute("""
            SELECT DISTINCT anno, sezione 
            FROM classe 
            WHERE anno_scolastico IS NOT NULL
        """)
        classes = cursor.fetchall()

    return render_template('manage_students.html', students=students, classes=classes)



@admin_bp.route('/delete_student/<student_username>', methods=['POST'])
@admin_required
def delete_student(student_username):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM alunno WHERE username = %s", (student_username,))
        conn.commit()
    return redirect(url_for('admin.manage_students'))


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
    academic_year = request.args.get('academic_year')

    if not academic_year:
        return redirect(url_for('admin.select_academic_year'))  # If no academic year is selected, redirect to the year selection page

    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        
        # Fetch students based on the selected academic year
        cursor.execute("SELECT * FROM alunno WHERE anno_scolastico = %s", (academic_year,))
        students = cursor.fetchall()

        # Fetch available classes (anno and sezione combinations) for the selected academic year
        cursor.execute("""
            SELECT DISTINCT anno, sezione 
            FROM classe 
            WHERE anno_scolastico = %s
        """, (academic_year,))
        classes = cursor.fetchall()

    return render_template('manage_students.html', students=students, classes=classes, academic_year=academic_year)

@admin_bp.route('/select_academic_year', methods=['GET', 'POST'])
@admin_required
def select_academic_year():
    if request.method == 'POST':
        academic_year = request.form['academic_year']
        return redirect(url_for('admin.manage_students', academic_year=academic_year))

    # Fetch all academic years from the database (if you have a table for this)
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT DISTINCT anno_scolastico FROM anno_scolastico")
        academic_years = cursor.fetchall()

    return render_template('select_academic_year.html', academic_years=academic_years)


@admin_bp.route('/add_student', methods=['POST'])
@admin_required
def add_student():
    username = request.form['username']
    nome = request.form['nome']
    cognome = request.form['cognome']
    password = request.form['password']
    selected_class = request.form['class']
    anno, sezione = selected_class.split('_')
    academic_year = request.form['academic_year']  # Get academic year from the form

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO alunno (username, nome, cognome, password, anno_scolastico, anno, sezione) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
            (username, nome, cognome, password, academic_year, anno, sezione)
        )
        conn.commit()
    return redirect(url_for('admin.manage_students', academic_year=academic_year))


@admin_bp.route('/delete_student/<student_username>', methods=['POST'])
@admin_required
def delete_student(student_username):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM alunno WHERE username = %s", (student_username,))
        conn.commit()
    return redirect(url_for('admin.manage_students'))
@admin_bp.route('/edit_student/<student_username>', methods=['GET', 'POST'])
@admin_required
def edit_student(student_username):
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)

        # Fetch the student data
        cursor.execute("SELECT * FROM alunno WHERE username = %s", (student_username,))
        student = cursor.fetchone()

        # Fetch the available classes for the student's academic year (anno_scolastico)
        cursor.execute("""
            SELECT DISTINCT anno, sezione 
            FROM classe 
            WHERE anno_scolastico = %s
        """, (student['anno_scolastico'],))
        classes = cursor.fetchall()

        if request.method == 'POST':
            nome = request.form['nome']
            cognome = request.form['cognome']
            password = request.form['password']
            selected_class = request.form['class']
            anno, sezione = selected_class.split('_')  # Split class into year and section
            
            cursor.execute(
                "UPDATE alunno SET nome = %s, cognome = %s, password = %s, anno = %s, sezione = %s WHERE username = %s",
                (nome, cognome, password, anno, sezione, student_username)
            )
            conn.commit()
            return redirect(url_for('admin.manage_students'))

    return render_template('edit_student.html', student=student, classes=classes)

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
    return redirect(url_for('admin.manage_professors'))

@admin_bp.route('/delete_professor/<professor_username>', methods=['POST'])
@admin_required
def delete_professor(professor_username):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM professore WHERE username = %s", (professor_username,))
        conn.commit()
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
    cursor.execute("SELECT DISTINCT anno_scolastico FROM anno_scolastico")
    academic_years = cursor.fetchall()
    conn.close()

    return render_template('manage_classes.html', academic_years=academic_years)

@admin_bp.route('/add_academic_year', methods=['POST'])
@admin_required
def add_academic_year():
    new_academic_year = request.form.get('new_academic_year')

    if new_academic_year:
        # Add the new academic year to the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO anno_scolastico (anno_scolastico) VALUES (%s)", (new_academic_year,))
        conn.commit()
        conn.close()
        
        flash('Anno accademico aggiunto con successo!', 'success')
    else:
        flash('Per favore inserisci un anno accademico valido.', 'danger')

    return redirect(url_for('admin.manage_classes'))

















@admin_bp.route('/class_detail', methods=['GET'])
@admin_required
def class_detail():
    academic_year = request.args.get('academic_year')
    
    # Fetch classes for the selected academic year
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT anno, sezione FROM classe WHERE anno_scolastico = %s", (academic_year,))
    classes = cursor.fetchall()
    
    # Fetch all available academic years for dropdown
    cursor.execute("SELECT anno_scolastico FROM anno_scolastico")
    academic_years = cursor.fetchall()
    
    conn.close()

    if request.method == 'POST':
        anno = request.form.get('anno')
        sezione = request.form.get('sezione')
        anno_scolastico = request.form.get('anno_scolastico')

        # Insert the new class into the database
        if anno and sezione and anno_scolastico:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO classe (anno, sezione, anno_scolastico) VALUES (%s, %s, %s)", 
                           (anno, sezione, anno_scolastico))
            conn.commit()
            conn.close()
            flash('Classe aggiunta con successo!', 'success')
            return redirect(url_for('admin.class_detail', academic_year=academic_year))
        else:
            flash('Per favore, completa tutti i campi.', 'danger')
    
    return render_template('class_detail.html', classes=classes, academic_year=academic_year, academic_years=academic_years)




@admin_bp.route('/add_class', methods=['POST'])
@admin_required
def add_class():
    anno = request.form.get('anno')
    sezione = request.form.get('sezione')
    anno_scolastico = request.form.get('anno_scolastico')
    
    # Insert the new class into the database
    if anno and sezione and anno_scolastico:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO classe (anno, sezione, anno_scolastico) VALUES (%s, %s, %s)", 
                       (anno, sezione, anno_scolastico))
        conn.commit()
        conn.close()
        flash('Classe aggiunta con successo!', 'success')
        return redirect(url_for('admin.class_detail', academic_year=anno_scolastico))  # redirect to class_detail page
    else:
        flash('Per favore, completa tutti i campi.', 'danger')
        return redirect(url_for('admin.class_detail', academic_year=anno_scolastico))

@admin_bp.route('/students_in_class/<string:academic_year>/<int:anno>/<string:sezione>', methods=['GET', 'POST'])
@admin_required
def students_in_class(academic_year, anno, sezione):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Handle adding a student to the class
    if request.method == 'POST':
        if 'add_student' in request.form:
            student_username = request.form.get('student_username')
            # Remove the student from any other class in the same academic year
            cursor.execute("""
                UPDATE alunno 
                SET anno_scolastico = NULL, anno = NULL, sezione = NULL 
                WHERE username = %s AND anno_scolastico = %s
            """, (student_username, academic_year))
            # Add the student to the selected class
            cursor.execute("""
                UPDATE alunno 
                SET anno_scolastico = %s, anno = %s, sezione = %s 
                WHERE username = %s
            """, (academic_year, anno, sezione, student_username))
            conn.commit()

        if 'remove_student' in request.form:
            student_username = request.form.get('remove_student_username')
            # Remove the student from the current class
            cursor.execute("""
                UPDATE alunno 
                SET anno_scolastico = NULL, anno = NULL, sezione = NULL 
                WHERE username = %s
            """, (student_username,))
            conn.commit()

    # Fetch students in the class
    cursor.execute("""
        SELECT username, nome, cognome 
        FROM alunno 
        WHERE anno_scolastico = %s AND anno = %s AND sezione = %s
    """, (academic_year, anno, sezione))
    students_in_class = cursor.fetchall()

    # Fetch all students who are not currently in this class
    cursor.execute("""
        SELECT username, nome, cognome 
        FROM alunno 
        WHERE anno_scolastico IS NULL OR (anno <> %s OR sezione <> %s)
    """, (anno, sezione))
    available_students = cursor.fetchall()

    conn.close()
    
    return render_template('students_in_class.html', 
                           students=students_in_class, 
                           available_students=available_students, 
                           academic_year=academic_year, 
                           anno=anno, 
                           sezione=sezione)

# utils.py
from database import get_db_connection
import datetime

def get_user_type(username):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT 'professore' as type FROM professore WHERE username = %s UNION ALL SELECT 'alunno' as type FROM alunno WHERE username = %s", (username, username))
    result = cursor.fetchone()
    
    conn.close()
    return result['type'] if result else None


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


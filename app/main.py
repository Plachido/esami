# main.py
from flask import Flask
from config import SECRET_KEY
from auth.auth_routes import auth_bp
from professor.professor_routes import professor_bp
from student.student_routes import student_bp

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(professor_bp, url_prefix='/professor')
app.register_blueprint(student_bp, url_prefix='/student')

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask

def create_app():
    app = Flask(__name__)
    app.secret_key = 'supersecretkey'  # Use a strong secret key in production

    # Import and register Blueprints
    from .student import student_bp
    from .professor import professor_bp

    app.register_blueprint(student_bp)
    app.register_blueprint(professor_bp)

    return app

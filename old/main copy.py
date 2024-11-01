
import csv
import random
import mysql.connector
from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
import datetime  # Import datetime for handling dates

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Use a strong secret key in production

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="professore"
    )

# Check if the user is a professor or student


@app.route('/')
def index():
    return render_template('login.html')








from flask import session, request, redirect, url_for, render_template, flash
import random



if __name__ == '__main__':
    app.run(debug=True)

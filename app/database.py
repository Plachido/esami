# database.py
import mysql.connector
from config import DB_CONFIG

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG, auth_plugin='mysql_native_password', use_pure=True)

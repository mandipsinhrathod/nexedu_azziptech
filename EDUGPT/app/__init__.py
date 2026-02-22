from flask import Flask
from config import Config
import mysql.connector

app = Flask(__name__)
app.config.from_object(Config)

def get_db_connection():
    conn = mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )
    return conn

from app import routes

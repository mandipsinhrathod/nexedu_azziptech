import mysql.connector
import os
from config import Config

def init_database():
    try:
        # Connect to MySQL Server (no database selected yet)
        print("Connecting to MySQL server...")
        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD
        )
        cursor = conn.cursor()

        # Create Database
        print(f"Creating database '{Config.MYSQL_DB}' if it doesn't exist...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DB}")
        
        # Select Database
        conn.database = Config.MYSQL_DB
        print(f"Connected to database '{Config.MYSQL_DB}'.")

        # Read Schema File
        schema_path = os.path.join(os.path.dirname(__file__), 'app', 'database', 'schema.sql')
        print(f"Reading schema from {schema_path}...")
        
        with open(schema_path, 'r') as f:
            schema_sql = f.read()

        # Execute Schema (split by ;)
        commands = schema_sql.split(';')
        for command in commands:
            if command.strip():
                try:
                    cursor.execute(command)
                except Exception as e:
                    print(f"Error executing command: {e}")
        
        conn.commit()
        print("Database schema initialized successfully!")
        
        cursor.close()
        conn.close()
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        print("Please ensure your MySQL server (e.g., XAMPP) is running and the credentials in .env are correct.")

if __name__ == '__main__':
    init_database()

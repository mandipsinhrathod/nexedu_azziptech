
import mysql.connector
from config import Config
import random

def populate_dashboard():
    try:
        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        cursor = conn.cursor()

        # Get the first user (assuming ID 1 is the main user for testing)
        cursor.execute("SELECT id FROM users LIMIT 1")
        user = cursor.fetchone()
        
        if not user:
            print("No users found. Please sign up first.")
            return

        user_id = user[0]
        print(f"Populating courses for User ID {user_id}...")

        # Sample Courses to Add
        sample_courses = [
            ("Advanced Python Patterns", "Advanced", "Career", "Visual", 5),
            ("Web Development with Flask", "Intermediate", "Project-based", "Interactive", 8),
            ("Introduction to AI & ML", "Beginner", "Academic", "Text-based", 6),
            ("Digital Marketing 101", "Beginner", "Casual", "Visual", 4),
            ("Cybersecurity Fundamentals", "Intermediate", "Career", "Interactive", 7)
        ]

        for title, level, goal, style, num_modules in sample_courses:
            # 1. Create Course
            cursor.execute("""
                INSERT INTO courses (user_id, topic, level, goal, style) 
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, title, level, goal, style))
            course_id = cursor.lastrowid
            
            # 2. Create Syllabus Modules
            completed_count = random.randint(1, num_modules - 1) # Ensure some are completed
            
            for i in range(1, num_modules + 1):
                is_completed = 1 if i <= completed_count else 0
                cursor.execute("""
                    INSERT INTO syllabus (course_id, module_title, module_order, is_completed)
                    VALUES (%s, %s, %s, %s)
                """, (course_id, f"Module {i}: Key Concepts of {title}", i, is_completed))
                
                syllabus_id = cursor.lastrowid
                
                # Add a completed lesson for completed modules (for activity log)
                if is_completed:
                    cursor.execute("""
                        INSERT INTO lessons (syllabus_id, title, completed_at)
                        VALUES (%s, %s, NOW() - INTERVAL %s DAY)
                    """, (syllabus_id, f"Lesson {i}", random.randint(0, 7)))

        conn.commit()
        print("Successfully added 5 active courses with progress!")
        
        cursor.close()
        conn.close()

    except mysql.connector.Error as err:
        print(f"Error: {err}")

if __name__ == "__main__":
    populate_dashboard()

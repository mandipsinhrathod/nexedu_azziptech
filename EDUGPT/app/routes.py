from flask import render_template, request, redirect, url_for, session, jsonify, flash
import json
import random
import time
import os
import requests
from datetime import datetime, timedelta
from app import app, get_db_connection
from app.agents.curriculum_agent import CurriculumAgent
from app.agents.instructor_agent import InstructorAgent
from app.agents.assessment_agent import AssessmentAgent
from app.agents.analytics_agent import AnalyticsAgent
from app.catalog_data import CATALOG_COURSES

# Initialize Agents
curriculum_agent = CurriculumAgent()
instructor_agent = InstructorAgent()
assessment_agent = AssessmentAgent()
analytics_agent = AnalyticsAgent()

# --- Tiny Offline Knowledge Base ---
KNOWLEDGE_BASE = {
    "python": "Python is a high-level, interpreted programming language known for its readability and vast ecosystem. It's great for web dev, data science, and AI.",
    "javascript": "JavaScript is the programming language of the web. It runs in the browser and on servers via Node.js.",
    "html": "HTML (HyperText Markup Language) is the standard markup language for documents designed to be displayed in a web browser.",
    "css": "CSS (Cascading Style Sheets) is a style sheet language used for describing the presentation of a document written in HTML.",
    "sql": "SQL (Structured Query Language) is a standard language for storing, manipulating and retrieving data in databases.",
    "react": "React is a free and open-source front-end JavaScript library for building user interfaces based on components.",
    "flask": "Flask is a micro web framework written in Python. It is classified as a microframework because it does not require particular tools or libraries.",
    "django": "Django is a high-level Python web framework that encourages rapid development and clean, pragmatic design.",
    "ai": "Artificial Intelligence (AI) is intelligence demonstrated by machines, as opposed to the natural intelligence displayed by humans or animals.",
    "ml": "Machine Learning (ML) is a field of inquiry devoted to understanding and building methods that 'learn', that is, methods that leverage data to improve performance.",
    "git": "Git is a distributed version control system that tracks changes in any set of computer files.",
    "api": "An API (Application Programming Interface) is a way for two or more computer programs to communicate with each other.",
    "database": "A database is an organized collection of data, generally stored and accessed electronically from a computer system.",
    "algorithm": "An algorithm is a finite sequence of rigorous instructions, typically used to solve a class of specific problems or to perform a computation."
}

@app.route('/')
def index():
    return render_template('index.html', catalog_courses=CATALOG_COURSES)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user and user['password_hash'] == password: 
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Successfully logged in!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check existing
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            flash('Email already registered', 'warning')
            cursor.close()
            conn.close()
            return redirect(url_for('login'))
            
        cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)", (username, email, password))
        conn.commit()
        
        user_id = cursor.lastrowid
        session['user_id'] = user_id
        session['username'] = username
        
        cursor.close()
        conn.close()
        flash('Account created! Welcome to EduGPT.', 'success')
        return redirect(url_for('dashboard'))
        
    return render_template('signup.html')

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    user_id = session['user_id']
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        bio = request.form.get('bio', '')
        
        # Update user
        cursor.execute("UPDATE users SET username = %s, email = %s, bio = %s WHERE id = %s", (username, email, bio, user_id))
        conn.commit()
        session['username'] = username # Update session
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return render_template('edit_profile.html', user=user)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/start_course', methods=['POST'])
def start_course():
    if 'user_id' not in session:
        flash('Please login to create a personalized course.', 'info')
        return redirect(url_for('login'))

    user_id = session['user_id']
    topic = request.form['topic']
    level = request.form['level']
    goal = request.form['goal']
    style = request.form['style']
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # 2. Store Course Request
    cursor.execute(
        "INSERT INTO courses (user_id, topic, level, goal, style) VALUES (%s, %s, %s, %s, %s)",
        (user_id, topic, level, goal, style)
    )
    conn.commit()
    course_id = cursor.lastrowid
    
    # 3. Call Curriculum Agent
    syllabus_response = curriculum_agent.design_syllabus(topic, level, goal, style)
    
    try:
        start = syllabus_response.find('{')
        end = syllabus_response.rfind('}') + 1
        if start != -1 and end != -1:
            json_str = syllabus_response[start:end]
            syllabus_data = json.loads(json_str)
            modules = syllabus_data.get('modules', [])
        else:
             modules = [
                 {"title": "Introduction to " + topic, "order": 1, "desc": "Basics"},
                 {"title": "Core Concepts of " + topic, "order": 2, "desc": "Deep Dive"},
                 {"title": "Advanced Techniques", "order": 3, "desc": "Expert Level"},
                 {"title": "Real-world Project", "order": 4, "desc": "Application"},
             ]
    except Exception as e:
        print(f"Error parsing syllabus: {e}")
        modules = [
             {"title": "Module 1: Foundations", "order": 1},
             {"title": "Module 2: Application", "order": 2}
        ]

    # 5. Store Syllabus
    for mod in modules:
        cursor.execute(
            "INSERT INTO syllabus (course_id, module_title, module_order, learning_objectives) VALUES (%s, %s, %s, %s)",
            (course_id, mod.get('title', 'Untitled Module'), mod.get('order', 1), mod.get('desc', ''))
        )
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('view_syllabus', course_id=course_id))

@app.route('/syllabus/<int:course_id>')
def view_syllabus(course_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM courses WHERE id = %s", (course_id,))
    course = cursor.fetchone()
    
    cursor.execute("SELECT * FROM syllabus WHERE course_id = %s ORDER BY module_order", (course_id,))
    modules = cursor.fetchall()
    
    total_modules = len(modules)
    completed_count = 0
    active_found = False
    
    formatted_modules = []
    
    for m in modules:
        cursor.execute("SELECT completed_at FROM lessons WHERE syllabus_id = %s", (m['id'],))
        lesson = cursor.fetchone()
        is_lesson_done = True if lesson and lesson['completed_at'] else False
        is_quiz_done = True if m['is_completed'] else False
        
        status = 'locked'
        if m['is_completed']:
            status = 'completed'
            completed_count += 1
        elif not active_found:
            status = 'active'
            active_found = True
            
        formatted_modules.append({
            **m,
            'status': status,
            'lesson_done': is_lesson_done,
            'quiz_done': is_quiz_done
        })
    
    progress = int((completed_count / total_modules) * 100) if total_modules > 0 else 0
    
    cursor.close()
    conn.close()
    
    return render_template('syllabus.html', course=course, modules=formatted_modules, progress=progress)

@app.route('/lesson/<int:module_id>')
def view_lesson(module_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM syllabus WHERE id = %s", (module_id,))
    module = cursor.fetchone()
    
    cursor.execute("SELECT * FROM courses WHERE id = %s", (module['course_id'],))
    course = cursor.fetchone()
    
    cursor.execute("SELECT * FROM lessons WHERE syllabus_id = %s", (module_id,))
    lesson = cursor.fetchone()
    
    if not lesson:
        content = instructor_agent.teach_lesson(
            module['module_title'], 
            module['module_title'], 
            course['level'], 
            course['style']
        )
        
        cursor.execute(
            "INSERT INTO lessons (syllabus_id, title, content) VALUES (%s, %s, %s)",
            (module_id, module['module_title'], content)
        )
        conn.commit()
        cursor.execute("SELECT * FROM lessons WHERE syllabus_id = %s", (module_id,))
        lesson = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return render_template('lesson.html', lesson=lesson, module=module, course=course)

@app.route('/complete_lesson/<int:lesson_id>', methods=['POST'])
def complete_lesson(lesson_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) 
    cursor.execute("UPDATE lessons SET completed_at = NOW() WHERE id = %s", (lesson_id,))
    conn.commit()
    cursor.execute("SELECT syllabus_id FROM lessons WHERE id = %s", (lesson_id,))
    result = cursor.fetchone()
    syllabus_id = result['syllabus_id']
    cursor.close()
    conn.close()
    return redirect(url_for('view_quiz', module_id=syllabus_id))

@app.route('/final_exam/<int:course_id>')
def final_exam(course_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM courses WHERE id = %s", (course_id,))
    course = cursor.fetchone()
    cursor.close()
    conn.close()
    
    questions = [
        {'id': 1, 'text': f'What is a core principle of {course["topic"]}?', 'options': ['Complexity', 'Simplicity and Efficiency', 'Chaos', 'None'], 'correct': 1},
        {'id': 2, 'text': f'Why is {course["topic"]} widely used?', 'options': ['Because it is old', 'Because it solves real problems', 'It is not used', 'Random reasons'], 'correct': 1},
        {'id': 3, 'text': 'Which of these is a best practice?', 'options': ['Ignore errors', 'Write clean code', 'Skip testing', 'Use magic numbers'], 'correct': 1}
    ]
    
    return render_template('final_exam.html', course=course, questions=questions)

@app.route('/submit_final_exam/<int:course_id>', methods=['POST'])
def submit_final_exam(course_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE courses SET status = 'completed' WHERE id = %s", (course_id,))
    if 'user_id' in session:
         cursor.execute("UPDATE users SET learning_points = learning_points + 500 WHERE id = %s", (session['user_id'],))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('view_certificate', course_id=course_id))

@app.route('/certificate/<int:course_id>')
def view_certificate(course_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM courses WHERE id = %s", (course_id,))
    course = cursor.fetchone()
    user = None
    if 'user_id' in session:
        cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
        user = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('certificate.html', course=course, user=user)

@app.route('/quiz/<int:module_id>')
def view_quiz(module_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM syllabus WHERE id = %s", (module_id,))
    module = cursor.fetchone()
    cursor.execute("SELECT * FROM courses WHERE id = %s", (module['course_id'],))
    course = cursor.fetchone()
    topic = module['module_title']
    questions = [
        {
            'id': 1,
            'text': f"Which of the following best describes the core concept of '{topic}'?",
            'options': [
                f"It is a method to ignore {topic}.", 
                f"It involves understanding the fundamental principles of {topic}.", 
                "It is completely unrelated to the course.", 
                "It is a type of food."
            ],
            'correct': 2
        },
        {
            'id': 2,
            'text': f"Why is '{topic}' important in {course['topic']}?",
            'options': [
                "It adds unnecessary complexity.", 
                "It is the only thing that matters.", 
                "It provides a foundation for advanced tasks.", 
                "It is deprecated."
            ],
            'correct': 3
        },
        {
            'id': 3,
            'text': "What would happen if you ignored this concept?",
            'options': [
                "Nothing, it is optional.", 
                "The system might fail or be inefficient.", 
                "You would become a wizard.", 
                "The computer would explode."
            ],
            'correct': 2
        }
    ]
    cursor.close()
    conn.close()
    return render_template('quiz.html', module=module, course=course, questions=questions)

@app.route('/submit_quiz/<int:module_id>', methods=['POST'])
def submit_quiz(module_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT course_id FROM syllabus WHERE id = %s", (module_id,))
    result = cursor.fetchone()
    course_id = result['course_id']
    cursor.execute("UPDATE syllabus SET is_completed = 1 WHERE id = %s", (module_id,))
    if 'user_id' in session:
        cursor.execute("UPDATE users SET learning_points = learning_points + 50 WHERE id = %s", (session['user_id'],))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Quiz Completed! +50 Points earned.', 'success')
    return redirect(url_for('view_syllabus', course_id=course_id))

@app.route('/assessment/<int:module_id>')
def view_assessment(module_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM syllabus WHERE id = %s", (module_id,))
    module = cursor.fetchone()
    quiz = assessment_agent.generate_quiz(module['module_title'], module['learning_objectives'])
    cursor.close()
    conn.close()
    return render_template('assessment.html', module=module, quiz=quiz)

@app.route('/submit_assessment/<int:module_id>', methods=['POST'])
def submit_assessment(module_id):
    flash("Assessment Submitted! Score: 85/100. Good usage of concepts.", "success")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT course_id FROM syllabus WHERE id = %s", (module_id,))
    row = cursor.fetchone()
    course_id = row[0] if row else 1
    cursor.close()
    conn.close()
    return redirect(url_for('view_syllabus', course_id=course_id))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/courses')
def public_courses():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM courses ORDER BY created_at DESC LIMIT 10")
    courses = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('public_courses.html', courses=courses)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/news')
def news():
    return render_template('news.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    
    cursor.execute("SELECT * FROM courses WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    raw_courses = cursor.fetchall()
    
    courses = []
    for c in raw_courses:
        cursor.execute("SELECT COUNT(*) as total FROM syllabus WHERE course_id = %s", (c['id'],))
        total = cursor.fetchone()['total']
        cursor.execute("SELECT COUNT(*) as completed FROM syllabus WHERE course_id = %s AND is_completed = 1", (c['id'],))
        completed = cursor.fetchone()['completed']
        progress = int((completed / total) * 100) if total > 0 else 0
        c_dict = dict(c)
        c_dict['progress'] = progress
        c_dict['total_modules'] = total
        c_dict['completed_modules'] = completed
        cursor.execute("SELECT module_title FROM syllabus WHERE course_id = %s ORDER BY module_order ASC", (c['id'],))
        syllabus_rows = cursor.fetchall()
        c_dict['syllabus_list'] = [row['module_title'] for row in syllabus_rows]
        courses.append(c_dict)
    
    cursor.execute("""
        SELECT l.title as lesson_title, c.topic as course_topic, l.completed_at 
        FROM lessons l 
        JOIN syllabus s ON l.syllabus_id = s.id 
        JOIN courses c ON s.course_id = c.id
        WHERE c.user_id = %s AND l.completed_at IS NOT NULL
        ORDER BY l.completed_at DESC LIMIT 5
    """, (user_id,))
    recent_activity = cursor.fetchall()
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=6)
    chart_labels = []
    chart_data = []
    current_check = start_date
    while current_check.date() <= end_date.date():
        day_str = current_check.strftime('%Y-%m-%d')
        chart_labels.append(current_check.strftime('%a')) 
        cursor.execute("""
            SELECT COUNT(l.id) as count 
            FROM lessons l 
            JOIN syllabus s ON l.syllabus_id = s.id 
            JOIN courses c ON s.course_id = c.id
            WHERE c.user_id = %s AND DATE(l.completed_at) = %s
        """, (user_id, day_str))
        count_res = cursor.fetchone()
        chart_data.append(count_res['count'] if count_res else 0)
        current_check += timedelta(days=1)
        
    streak = 0
    check_date = datetime.now()
    cursor.execute("""
        SELECT COUNT(l.id) as count FROM lessons l JOIN syllabus s ON l.syllabus_id = s.id JOIN courses c ON s.course_id = c.id WHERE c.user_id = %s AND DATE(l.completed_at) = %s
    """, (user_id, check_date.strftime('%Y-%m-%d')))
    today_count = cursor.fetchone()['count']
    if today_count > 0:
        streak += 1
        
    check_date -= timedelta(days=1)
    while True:
        cursor.execute("""
            SELECT COUNT(l.id) as count FROM lessons l JOIN syllabus s ON l.syllabus_id = s.id JOIN courses c ON s.course_id = c.id WHERE c.user_id = %s AND DATE(l.completed_at) = %s
        """, (user_id, check_date.strftime('%Y-%m-%d')))
        count = cursor.fetchone()['count']
        if count > 0:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break

    cursor.close()
    conn.close()
    
    return render_template('dashboard.html', 
        user=user, 
        courses=courses, 
        activity=recent_activity,
        chart_labels=json.dumps(chart_labels),
        chart_data=json.dumps(chart_data),
        streak=streak
    )

@app.route('/chat')
def chat_interface():
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.json
    user_message = data.get('message', '')
    agent = data.get('agent', 'Mentor Core')
    history = data.get('history', [])
    
    # 1. Agent Tool Usage (The "Connection")
    # If user wants a Syllabus/Course
    msg_lower = user_message.lower()
    
    # Tool: Curriculum Agent
    if any(word in msg_lower for word in ['syllabus', 'curriculum', 'course outline', 'learning path']):
        try:
            # Extract topic simply
            topic = user_message.replace('syllabus', '').replace('course', '').replace('create', '').strip()
            if not topic: topic = "Python Programming" # Default
            
            # Call the Actual Agent
            syllabus = curriculum_agent.design_syllabus(topic, "Intermedate", "Career", "Visual")
            
            # Format JSON to Markdown
            reply = f"""### 📘 Course Syllabus: {topic}

"""
            for mod in syllabus:
                reply += f"""**{mod.get('module_title', 'Module')}** ({mod.get('estimated_time', 'N/A')})
* {mod.get('learning_objectives', '')}

"""
                
            reply += "\n*(Generated by Curriculum Agent)*"
            return jsonify({'reply': reply})
        except Exception as e:
            print(f"Agent Error: {e}")
            # Fallthrouguh to normal chat

    # Tool: Instructor Agent (Teach)
    if any(word in msg_lower for word in ['teach me', 'explain', 'lesson on']):
        try:
            topic = user_message.replace('teach me', '').replace('explain', '').strip()
            if not topic: topic = "this concept"
            
            # Call Instructor Agent
            # Note: Instructor agent usually returns markdown structure
            content = instructor_agent.teach_lesson(topic, topic, "Beginner", "Interactive")
            
            # Clean up the response if it's raw JSON or just pass it
            reply = f"""### 🎓 Instructor: {topic}

{content}"""
            return jsonify({'reply': reply})
        except Exception as e:
            print(f"Instructor Error: {e}")

    # Tool: Assessment Agent (Quiz)
    if any(word in msg_lower for word in ['quiz', 'test me', 'assessment']):
        try:
            topic = user_message.replace('quiz', '').replace('test me', '').strip()
            if not topic: topic = "General Knowledge"
            
            quiz = assessment_agent.generate_quiz(topic, "General Evaluation")
            
            # Format Quiz
            reply = f"""### 📝 Quick Quiz: {topic}

"""
            if isinstance(quiz, list):
                for i, q in enumerate(quiz[:3]): # Limit to 3
                    reply += f"""**Q{i+1}: {q.get('question', 'Question?')}**
A) {q.get('options', [''])[0]}
B) {q.get('options', [''])[1]}

"""
            elif isinstance(quiz, str):
                 reply += quiz
                 
            return jsonify({'reply': reply})
        except Exception as e:
            print(f"Assessment Error: {e}")


    # Define Persona based on agent
    system_prompt = "You are a helpful AI assistant."
    if "Architect" in agent:
        system_prompt = "You are 'The Architect', an expert educational strategist. Tone: Professional, structured. Help the user plan their learning path."
    elif "Mentor" in agent:
        system_prompt = "You are 'Mentor Core', a patient teacher. Tone: Encouraging, clear. Use analogies to explain concepts."
    elif "Oracle" in agent:
        system_prompt = "You are 'The Oracle', a data-driven analyst. Tone: precise, robotic. Focus on efficiency and metrics."
    elif "Guardian" in agent:
        system_prompt = "You are 'Guardian', a fact-checker. Tone: Formal, protective. Verify facts rigorously."

    # --- Strategy 0: Grok AI ---
    grok_key = os.getenv('GROK_API_KEY')
    if grok_key and 'your_grok' not in grok_key:
        try:
            url = "https://api.x.ai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {grok_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "grok-beta",
                "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}],
                "max_tokens": 800
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=10)
            if resp.status_code == 200:
                result = resp.json()
                reply = result['choices'][0]['message']['content'].strip()
                return jsonify({'reply': reply + "\n\n*(Powered by Grok AI)*"})
            else:
                print(f"Grok Error: {resp.status_code} {resp.text}")
        except Exception as e:
            print(f"Grok Error: {e}")

    # Build full prompt history
    messages_payload = [{"role": "system", "content": system_prompt}]
    for msg in history:
        messages_payload.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
    
    # If the last message in history is the user message, we don't need to append again.
    # Frontend pushes user_message to history before sending.

    # --- Strategy 0.5: Groq AI ---
    groq_key = os.getenv('GROQ_API_KEY')
    if groq_key and 'your_groq' not in groq_key:
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {groq_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "llama3-8b-8192",
                "messages": messages_payload,
                "max_tokens": 1500
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=10)
            if resp.status_code == 200:
                result = resp.json()
                reply = result['choices'][0]['message']['content'].strip()
                return jsonify({'reply': reply + "\n\n*(Powered by Groq)*"})
            else:
                print(f"Groq Error: {resp.status_code} {resp.text}")
        except Exception as e:
            print(f"Groq Error: {e}")

    # --- Strategy 1: OpenAI ---
    openai_key = os.getenv('OPENAI_API_KEY')
    openai_error = None
    
    if openai_key and 'sk-' in openai_key and 'dev_key' not in openai_key:
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {openai_key}"}
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}],
                "max_tokens": 500
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=10)
            if resp.status_code == 200:
                result = resp.json()
                return jsonify({'reply': result['choices'][0]['message']['content'].strip()})
            else:
                openai_error = f"OpenAI Error: {resp.status_code} {resp.text}"
                # We do NOT return here, we fall through to Simulation so user gets a response
        except Exception as e:
            openai_error = str(e)

    # --- Strategy 2: Google Gemini ---
    gemini_key = os.getenv('GEMINI_API_KEY')
    
    if gemini_key and 'your_gemini' not in gemini_key:
        try:
            # Gemini Pro REST API
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={gemini_key}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [{
                    "parts": [{"text": f"System Instructions: {system_prompt}\n\nUser Question: {user_message}"}]
                }]
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=10)
            
            if resp.status_code == 200:
                result = resp.json()
                # Safe parsing of Gemini response
                if 'candidates' in result and len(result['candidates']) > 0:
                     reply = result['candidates'][0]['content']['parts'][0]['text']
                     return jsonify({'reply': reply + "\n\n*(Powered by Gemini)*"})
        except Exception as e:
            print(f"Gemini Error: {e}")

    # --- Strategy 3: Dynamic Simulation Engine (Smart Offline Mode) ---
    try:
        time.sleep(1.0) # Simulate thinking
        
        msg_lower = user_message.lower() if user_message else ""
        mock_reply = ""
        
        # 0. Check Offline Knowledge Base (Low-Tech Intelligence)
        found_knowledge = False
        for key, value in KNOWLEDGE_BASE.items():
            if key in msg_lower:
                mock_reply = f"""### 📘 {key.title()}
{value}

*(Offline Knowledge Base)*"""
                found_knowledge = True
                break
        
        if found_knowledge:
             return jsonify({'reply': mock_reply})

        # 1. Simple Confirmations/Negations
        if msg_lower in ['yes', 'yeah', 'sure', 'ok', 'okay']:
            mock_reply = "Great! Let's proceed. What specific topic should we focus on next?"
        elif msg_lower in ['no', 'nope', 'nah', 'cancel']:
             mock_reply = "Understood. Is there something else you'd like to discuss or a different angle you'd like to take?"
             
        # 2. Greetings
        elif any(word in msg_lower for word in ['hello', 'hi', 'hey', 'greetings', 'morning', 'evening']):
             if "Architect" in agent:
                 mock_reply = "Greetings. I am The Architect. I can help you design a comprehensive learning strategy. What is your goal?"
             elif "Mentor" in agent:
                 mock_reply = "Hello there! I'm Mentor Core. I'm here to explain difficult concepts in simple terms. What are we learning today?"
             elif "Oracle" in agent:
                 mock_reply = "System Online. The Oracle is ready to analyze your learning metrics. How can I optimize your progress?"
             elif "Guardian" in agent:
                 mock_reply = "Safety Protocols Active. Guardian here. I can verify facts and ensure content quality. Proceed."
             else:
                 mock_reply = "Hello! I am ready to assist you. How can I help?"

        # 3. Intent Detection: ROADMAP / PLAN
        elif any(word in msg_lower for word in ['roadmap', 'plan', 'path', 'curriculum', 'learn', 'start']):
            topic = "this subject"
            if "python" in msg_lower: topic = "Python Programming"
            elif "ai" in msg_lower or "ml" in msg_lower: topic = "Artificial Intelligence"
            elif "web" in msg_lower: topic = "Web Development"
            elif "data" in msg_lower: topic = "Data Science"
            
            mock_reply = f"""### 🚀 Learning Roadmap: {topic}
To master {topic}, I recommend this 4-week structured plan:

**Week 1: The Foundations**
*   Understand core syntax and variables
*   Control flow (If/Else, Loops)
*   *Project: Build a simple Calculator*

**Week 2: Data Structures**
*   Lists, Dictionaries, and Sets
*   Functions and Modules
*   *Project: To-Do List App*

**Week 3: Advanced Concepts**
*   Object-Oriented Programming (OOP)
*   File Handling & APIs
*   *Project: Weather Fetching Tool*

**Week 4: Real World Application**
*   Frameworks (e.g., Flask, Pandas)
*   Final Capstone Project
            
**Would you like resources for Week 1?**"""

        # 4. Intent Detection: EXPLAIN / WHAT IS
        elif any(word in msg_lower for word in ['explain', 'what is', 'how to', 'define', 'concept', 'mean']):
            concept = "the concept"
            if "python" in msg_lower: concept = "Python"
            elif "variable" in msg_lower: concept = "Variables"
            elif "function" in msg_lower: concept = "Functions"
            elif "api" in msg_lower: concept = "APIs"
            elif "list" in msg_lower: concept = "Lists"
            
            mock_reply = f"""### 💡 Understanding {concept}
To explain **{concept}** simply:
            
Imagine {concept} as a tool in your digital toolbox. It allows you to structure data and logic effectively. 
            
*   **Key Benefit:** It saves time and reduces errors.
*   **Real World Analogy:** Think of it like a recipe because you explicitly state ingredients to get a result.
            
**Shall I show you a code example?**"""

        # 5. Intent Detection: CODE / EXAMPLE
        elif any(word in msg_lower for word in ['code', 'example', 'syntax', 'script', 'program']):
            lang = "python"
            if "javascript" in msg_lower or "js" in msg_lower: lang = "javascript"
            elif "html" in msg_lower: lang = "html"
            elif "sql" in msg_lower: lang = "sql"
            
            code_snippet = ""
            if lang == "python":
                code_snippet = "def greet(name):\n    return f'Hello, {name}!'\n\nprint(greet('Student'))"
            elif lang == "javascript":
                code_snippet = "function greet(name) {\n    console.log(`Hello, ${name}!`);\n}\ngreet('Student');"
            elif lang == "sql":
                code_snippet = "SELECT * FROM users WHERE active = 1;"
                
            mock_reply = f"""Here is a simple **{lang.title()}** example for you:

```{lang}
{code_snippet}
```

Try running this in your local environment!"""

        # 6. Smart Fallback (Prevent Parrot Mode)
        else:
             # Check for short, ambiguous messages
            if len(user_message) < 5:
                mock_reply = "Could you elaborate on that? I want to make sure I understand correctly."
            else:
                # Default Agent Responses (Enhanced)
                if "Architect" in agent:
                    mock_reply = f"I've noted your input on '{user_message[:20]}...'. To provide the best strategy, what is your ultimate career goal?"
                elif "Mentor" in agent:
                    mock_reply = f"That's interesting. Regarding '{user_message[:20]}...', which specific part feels most challenging to you right now?"
                elif "Oracle" in agent:
                    mock_reply = f"Data point received: '{user_message[:20]}...'. I am cross-referencing this with your learning history. Please continue."
                elif "Guardian" in agent:
                    mock_reply = f"I have processed your statement. Please provide more context or specific evidence so I can verify this claim."
                 
        return jsonify({'reply': mock_reply})
        
    except Exception as e:
        print(f"Simulation Error: {e}")
        return jsonify({'reply': "I apologize, my neural link is stabilizing. Please try asking again in a moment."})

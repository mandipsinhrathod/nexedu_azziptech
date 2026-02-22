import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import Groq from 'groq-sdk';
import mysql from 'mysql2/promise';
import bcrypt from 'bcrypt';

dotenv.config();

// Create MySQL connection pool
const db = mysql.createPool({
    host: process.env.DB_HOST || 'localhost',
    user: process.env.DB_USER || 'root',
    password: process.env.DB_PASSWORD || '',
    database: process.env.DB_NAME || 'mandip_edu',
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0
});

const app = express();
app.use(cors());
app.use(express.json());

const groq = new Groq({ apiKey: process.env.GROQ_API_KEY });

const AGENT_PROMPTS = {
    CurriculumArchitect: `You are the Curriculum Architect for NexEdu. Your job is to analyze the user's input topic, determine their learning level (Beginner/Intermediate/Advanced) based on context, and generate a highly structured syllabus. Provide output formatted with:
1. Learning Level Identification
2. Structured Syllabus Overview (ranging from Beginner mechanics to Research level physics). Make it futuristic and rigorous.`,
    ResearchPhysicist: `You are the Research Physicist for NexEdu. Your job is to provide the Mathematical Foundation and core scientific principles of the current topic. Never oversimplify. Include physics equations (e.g. F = G(m₁m₂)/r²) with full variable explanation, step-by-step reasoning on space-time curvature or relevant principles.`,
    AdaptiveInstructor: `You are the Adaptive Instructor for NexEdu. Your job is to detect the user's clarity needs. Provide Real-World Applications of the advanced physics concepts taught. Break down complex things into understandable yet rigorous analogues that a future scientist would appreciate.`,
    AssessmentDesigner: `You are the Assessment Designer for NexEdu. Provide a rigorous Assessment Section for the given topic:
1. 3 Conceptual Questions
2. 2 Numerical Problems
3. 1 Higher-Order Critical Thinking Challenge`,
    InnovationCatalyst: `You are the Innovation Catalyst for NexEdu. Your job is to propose a Futuristic Exploration & Innovation Challenge based precisely on the topic and scientifically responsible applications (e.g., gravity-controlled propulsion, artificial gravity). Encourage research-driven mindset.`,
    ProgressAnalyst: `You are the Progress Analyst for NexEdu. Generate a highly visual and impressive student 'Report Card' in pure Markdown. Evaluate mastery signals based on context and provide:
1. An introduction summarizing their growth.
2. A beautiful Markdown Table titled "Learning Analytics" showing modules/sub-topics and a calculated Score (e.g. 92%, 85%) with a Status (e.g., Novice, Competent, Master).
3. A visual "Mastery Progress" section. You MUST format this strictly as a vertical bulleted Markdown list using emoji blocks (e.g., \`- 🟩🟩🟩🟩⬛ 80% - Concept Name\`) so each concept is comfortably on its own line.
4. Progress Recommendation (advancement, revision, or skill-level update).`,
    CertificationAuthority: `You are the Certification Authority for NexEdu. Provide the absolute Final Certification Exam based on the entire topic context.
Generate a comprehensive test containing:
1. 3 rigorous multiple-choice questions testing the breadth of the topic.
2. 2 short-answer scenario problems requiring deep thought.
Wait for the student to provide answers. If the student answers the questions, evaluate them strictly.
If they score above 80%, generate a beautiful pure Markdown "Certificate of Mastery" highlighting their achievement, the topic, and encouraging them to keep learning.`
};

app.post('/api/chat', async (req, res) => {
    try {
        const { agentId, messageHistory } = req.body;

        if (!AGENT_PROMPTS[agentId]) {
            return res.status(400).json({ error: 'Invalid agent ID' });
        }

        // Build the messages payload: System prompt + full chat history
        let messages = [{ role: "system", content: AGENT_PROMPTS[agentId] }];
        if (Array.isArray(messageHistory)) {
            messages = messages.concat(messageHistory);
        }

        console.log("SENDING REQUEST TO GROQ:", JSON.stringify(messages, null, 2));

        const completion = await groq.chat.completions.create({
            messages: messages,
            model: "llama-3.3-70b-versatile",
            temperature: 0.7,
            max_tokens: 2048,
        });

        res.json({ content: completion.choices[0].message.content });
    } catch (error) {
        console.error("Groq Error details:", error.error || error.message || error);
        res.status(500).json({ error: 'Failed to communicate with Groq API', message: error.message });
    }
});

// Authentication Endpoints
app.post('/api/register', async (req, res) => {
    try {
        const { name, email, password } = req.body;
        if (!name || !email || !password) {
            return res.status(400).json({ error: 'All fields are required.' });
        }

        // Check if user already exists
        const [existing] = await db.query('SELECT * FROM users WHERE email = ?', [email]);
        if (existing.length > 0) {
            return res.status(400).json({ error: 'Email already registered.' });
        }

        const hashedPassword = await bcrypt.hash(password, 10);

        const [result] = await db.query(
            'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
            [name, email, hashedPassword]
        );

        res.status(201).json({ message: 'User created successfully', user: { id: result.insertId, name, email } });
    } catch (err) {
        console.error("Registration Error:", err);
        res.status(500).json({ error: 'Database error during registration.' });
    }
});

app.post('/api/login', async (req, res) => {
    try {
        const { email, password } = req.body;
        if (!email || !password) {
            return res.status(400).json({ error: 'Email and password are required.' });
        }

        const [users] = await db.query('SELECT * FROM users WHERE email = ?', [email]);
        if (users.length === 0) {
            return res.status(401).json({ error: 'Invalid credentials.' });
        }

        const user = users[0];
        const isMatch = await bcrypt.compare(password, user.password_hash);

        if (!isMatch) {
            return res.status(401).json({ error: 'Invalid credentials.' });
        }

        res.json({ message: 'Login successful', user: { id: user.id, name: user.username, email: user.email } });
    } catch (err) {
        console.error("Login Error:", err);
        res.status(500).json({ error: 'Database error during login.' });
    }
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
    console.log(`NexEdu Backend Server running on port ${PORT}`);
});

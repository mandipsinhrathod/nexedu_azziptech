# 🚀 NexEdu (formerly EduGPT) - Technical Documentation

Welcome to the official documentation for **NexEdu**, a next-generation, AI-driven educational platform designed to provide an autonomous, personalized learning experience through a multi-agent cognitive architecture.

---

## 📖 1. Project Overview

NexEdu is an enterprise-grade AI-driven educational ecosystem engineered to deliver structured, adaptive, and research-oriented learning experiences. Unlike conventional chatbot systems, NexEdu operates through a modular multi-agent cognitive architecture that orchestrates specialized AI roles across the complete learning lifecycle.

By decoupling the AI engine from traditional single-prompt UI constraints, NexEdu routes students through a specialized pedagogical pipeline—from dynamic syllabus generation and rigorous theoretical deep-dives, to interactive assessments and automated markdown certification.

The application rests on a modern, high-performance tech stack utilizing a React/Vite frontend with a premium **Dark Glassmorphism** aesthetic, robust secure authentication, and a fully decoupled Node.js API powered by the lightning-fast Groq LLM inference engine.

---

## 🏗️ 2. Architectural Stack

NexEdu is built using a modern decoupled client-server architecture.

### **Frontend (Client)**
*   **Framework:** React + Vite
*   **Styling:** Pure CSS (Custom Dark Glassmorphism theme, CSS Animations)
*   **Icons:** Lucide-React
*   **Markdown Parsing:** `react-markdown` + `remark-gfm` for rendering GitHub-flavored markdown and tables natively in chat.
*   **State Management:** React Hooks (`useState`, `useEffect`, `useRef`)

### **Backend (API Server)**
*   **Environment:** Node.js
*   **Framework:** Express.js
*   **AI Engine Integration:** Groq SDK (`llama-3.3-70b-versatile` model for ultra-fast, high-token completions)
*   **Security:** `bcrypt` for cryptographic password hashing, `cors` for cross-origin management.

### **Database**
*   **Database Engine:** MySQL (`mysql2` promise wrapper for async queries)
*   **Schema:** `mandip_edu` database containing a `users` table for authentication.

### **Integrated Python Hub (Legacy EduGPT)**
*   **Framework:** Flask
*   **Purpose:** Houses the legacy EduGPT landing page and additional python-based features. Runs concurrently alongside the Node application.

---

## 🧠 3. The Multi-Agent Cognitive System

The core innovation of NexEdu is its modular prompt injection system. The backend (`server.js`) maintains a dictionary `AGENT_PROMPTS` that defines strict roles for the LLM based on the user's current stage in the learning lifecycle.

**The Pipeline:**
1.  **Curriculum Architect:** Analyzes initial topic input and determines the user's learning level to generate a structured syllabus.
2.  **Research Physicist (Core Teacher):** Delivers rigorous mathematical and theoretical foundations. Refuses to oversimplify.
3.  **Adaptive Instructor (Practical Guide):** Translates the deep theory into real-world applications and understandable analogies.
4.  **Assessment Designer (Quiz Master):** Dynamically generates a mix of conceptual, numerical, and critical-thinking questions.
5.  **Innovation Catalyst (Future Explorer):** Pushes the boundaries of the topic by proposing futuristic, research-driven challenges.
6.  **Progress Analyst (Growth Tracker):** Evaluates the user's chat history and generates a styled Markdown "Report Card" featuring an emoji-based mastery progress bar.
7.  **Certification Authority:** Administers a rigorous final exam based on the entire session's context. Automatically generates a formal Markdown **"Certificate of Mastery"** upon achieving a score >80%.

**Context Injection (`App.jsx`):**
When switching between agents, the React frontend automatically prepends the previous agent's final output as hidden `[System Context]` to the new agent's prompt. This prevents "AI Amnesia" and ensures a seamless pedagogical flow.

---

## 🎨 4. User Interface & Design System

The application employs a meticulously crafted aesthetic focused on focus and immersion.

*   **Color Palette:** Deep navy/slate background (`#0b0f19`) contrasted with vibrant, glowing neons (Cyan, Blue, Purple).
*   **Frosted Glass Effect:** Extensive use of `rgba()` backgrounds paired with `backdrop-filter: blur(12px)` to create translucent, floating UI panels.
*   **Dynamic Visuals:** 
    *   **Agent Avatars:** Instead of static logos, active chats display animated, glowing SVG icons specific to the active AI module.
    *   **Pulse Animations:** CSS keyframe animations (e.g., `pulse-anim`, `floatIcon`) simulate a "live" heartbeat effect when agents are active.

---

## 🚀 5. Local Setup & Installation

To run the complete NexEdu ecosystem locally:

### **Prerequisites**
*   Node.js (v18+)
*   Python (3.9+)
*   XAMPP (or standalone MySQL Server)
*   Groq API Key

### **Step 1: Database Initialization**
1.  Start MySQL via the XAMPP Control Panel.
2.  Execute the `setup_database.sql` script to create the `mandip_edu` database and `users` table.

### **Step 2: Environment Configuration**
Create a `.env` file in the root `demoedu` directory:
```env
GROQ_API_KEY=your_groq_api_key_here
PORT=5001
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=mandip_edu
```

### **Step 3: Booting the Servers**
You require three terminal instances to run the full environment:

**Terminal 1 (Node API):**
```bash
cd demoedu
node server.js
```
*(Runs on port 5001)*

**Terminal 2 (React UI):**
```bash
cd demoedu
npm run dev
```
*(Runs on port 5173)*

**Terminal 3 (Python EduGPT Hub):**
```bash
cd demoedu/EDUGPT
.\.venv\Scripts\activate
python run.py
```
*(Runs on port 5000)*

---

## 🔮 6. Future Roadmap

1.  **Persistent Chat Histories:** Migrating React state history into a dedicated MySQL `chat_sessions` table to allow users to pause and resume learning paths across different devices.
2.  **Live Token Streaming:** Implementing `.create({ stream: true })` on the Groq API calls to enable real-time typewriter visual effects on the frontend.
3.  **JWT Authentication:** Replacing standard local state auth with JSON Web Tokens (JWT) for robust, persistent session security.

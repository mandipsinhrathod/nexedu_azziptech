import Groq from 'groq-sdk';
import dotenv from 'dotenv';
dotenv.config();

const groq = new Groq({ apiKey: process.env.GROQ_API_KEY });

async function test() {
    try {
        const res = await groq.chat.completions.create({
            messages: [
                { role: "system", content: "You are a test agent." },
                { role: "user", content: "Hello" }
            ],
            model: "llama-3.3-70b-versatile",
            temperature: 0.7,
            max_tokens: 100
        });
        console.log("Success:", res.choices[0].message.content);
    } catch (err) {
        console.error("Error:", err.error || err);
    }
}

test();

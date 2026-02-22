import os
import openai
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.grok_api_key = os.getenv("GROK_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key
        
    def generate_completion(self, prompt, system_role="You are a helpful AI assistant."):
        """
        Generates completion from LLM. Defaults to mock if no API key is set.
        """
        has_grok = (self.grok_api_key and "your_grok" not in self.grok_api_key)
        has_groq = (self.groq_api_key and "your_groq" not in self.groq_api_key)
        has_openai = (self.api_key and "your_openai" not in self.api_key)
        
        if not has_grok and not has_groq and not has_openai:
            print(f"No API Key found. Returning mock response for role: {system_role}")
            return self._mock_response(prompt, system_role)
            
        if has_grok:
            try:
                import requests
                url = "https://api.x.ai/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {self.grok_api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": "grok-beta",
                    "messages": [
                        {"role": "system", "content": system_role},
                        {"role": "user", "content": prompt}
                    ]
                }
                resp = requests.post(url, headers=headers, json=payload, timeout=20)
                if resp.status_code == 200:
                    return resp.json()['choices'][0]['message']['content']
                else:
                    print(f"Grok Error: {resp.status_code} {resp.text}")
                    # fallback to next options if any or return error
            except Exception as e:
                print(f"Grok LLM Error: {e}")
        
        if has_groq:
            try:
                import requests
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {self.groq_api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": "llama3-8b-8192",
                    "messages": [
                        {"role": "system", "content": system_role},
                        {"role": "user", "content": prompt}
                    ]
                }
                resp = requests.post(url, headers=headers, json=payload, timeout=20)
                if resp.status_code == 200:
                    return resp.json()['choices'][0]['message']['content']
                else:
                    print(f"Groq Error: {resp.status_code} {resp.text}")
            except Exception as e:
                print(f"Groq LLM Error: {e}")
                
        try:
            response = openai.chat.completions.create(
                model="gpt-4o", # Or gpt-3.5-turbo
                messages=[
                    {"role": "system", "content": system_role},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"LLM Error: {e}")
            return f"Error contacting AI service: {e}"

    def _mock_response(self, prompt, system_role):
        """
        Simple mock responses based on keywords in the prompt to simulate the agent behavior
        without an API key.
        """
        import re
        prompt_lower = prompt.lower()
        
        # Try to extract topic from prompt (e.g., "on 'Python'")
        topic_match = re.search(r"on '([^']+)'", prompt)
        topic = topic_match.group(1) if topic_match else "the Topic"
        
        if "generate a course syllabus" in prompt_lower or "create a structured syllabus" in prompt_lower:
            # Return JSON for CurriculumAgent
            return f"""
```json
[
    {{
        "module_title": "Introduction to {topic}",
        "learning_objectives": "Understand the core principles and setup environment for {topic}.",
        "estimated_time": "30 mins"
    }},
    {{
        "module_title": "Core Concepts of {topic}",
        "learning_objectives": "Deep dive into the fundamental syntax and structure.",
        "estimated_time": "45 mins"
    }},
    {{
        "module_title": "Advanced {topic} Strategies",
        "learning_objectives": "Mastering complex techniques and best practices.",
        "estimated_time": "60 mins"
    }},
    {{
        "module_title": "Real-World Application: {topic}",
        "learning_objectives": "Applying knowledge to build a practical project.",
        "estimated_time": "90 mins"
    }},
    {{
        "module_title": "Final Review & Assessment",
        "learning_objectives": "Reviewing key concepts and testing proficiency.",
        "estimated_time": "30 mins"
    }}
]
```
"""
        elif "explain" in prompt_lower or "teach" in prompt_lower:
             return f"""
### Topic: {topic}

**Explanation**: 
{topic} is a fundamental concept that enables you to solve specific problems efficiently. It involves understanding the underlying structure and applying it to real-world scenarios.

**Analogy**: 
Think of {topic} like a tool in a toolbox. Just as a hammer is used for nails, {topic} is used for specific tasks in this domain.

**Key Concepts**:
1. **Foundation**: The basic building blocks of {topic}.
2. **Application**: How to use {topic} in practice.
3. **Optimization**: Making {topic} work better and faster.

**Example**:
If you were building a house, {topic} would be the blueprint that ensures everything is stable.

**Checkpoint Question**:
How does {topic} improve the overall efficiency of the system?
"""
        elif "quiz" in prompt_lower or "assessment" in prompt_lower:
             return """
1. **MCQ**: What is the correct file extension for Python files?
   A) .pyth
   B) .pt
   C) .py
   D) .p
   *Correct Answer: C*

2. **Short Answer**: implementing a function in Python requires which keyword?
"""
        return "Simulated AI Response. Please configure OpenAI API Key for real intelligence."

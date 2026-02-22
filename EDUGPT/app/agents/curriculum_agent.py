from app.agents.base_agent import BaseAgent
import json

class CurriculumAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            role="Curriculum Designer Agent",
            system_instruction=(
                "You are responsible for creating structured learning paths. "
                "Given a topic, level, goal, and style, generate a Course Title, Description, "
                "and 5-10 modules (with learning objectives, key concepts, practical tasks, mini projects, estimated time). "
                "Format the output strictly as a structured JSON or clear text blocks."
            )
        )

    def design_syllabus(self, topic, level, goal, style):
        import json
        
        # Generate real syllabus using LLM
        prompt = f"""
        Create a structured syllabus for a {level} level course on '{topic}'.
        Focus on a '{style}' learning style.
        Generate 5 distinct modules.
        Format the output strictly as a JSON list of objects, where each object has:
        - module_title: A clear title.
        - learning_objectives: 2 sentences on what will be learned.
        - estimated_time: e.g. "30 mins"
            
        Example Format:
        [
            {{"module_title": "Introduction to {topic}", "learning_objectives": "Learn the basics...", "estimated_time": "30 mins"}},
            ...
        ]
        """
            
        response = self.generate_response(prompt)
        
        try:
            # cleaner logic
            json_str = response.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0]
            
            syllabus_data = json.loads(json_str)
        except:
            # Fallback if AI fails
            syllabus_data = [
                {"module_title": f"Introduction to {topic}", "learning_objectives": "Basics and Setup", "estimated_time": "30 mins"},
                {"module_title": f"Core Concepts of {topic}", "learning_objectives": "Deep Dive into syntax", "estimated_time": "45 mins"},
                {"module_title": f"Advanced {topic} Techniques", "learning_objectives": "Complex patterns", "estimated_time": "60 mins"},
                {"module_title": f"Real-world Project: {topic}", "learning_objectives": "Building an app", "estimated_time": "90 mins"},
                {"module_title": "Final Review & Deployment", "learning_objectives": "Sharing your work", "estimated_time": "30 mins"}
            ]
            
        return syllabus_data

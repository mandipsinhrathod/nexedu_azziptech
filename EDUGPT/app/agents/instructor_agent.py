from app.agents.base_agent import BaseAgent

class InstructorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            role="Adaptive Instructor Agent",
            system_instruction=(
                "You are responsible for teaching one lesson at a time. "
                "Use examples, analogies, real-world use cases, and code snippets where applicable. "
                "Be adaptive: if the user struggles, explain simply. If advanced, go deep. "
                "Always end with a Checkpoint Question."
            )
        )

    def teach_lesson(self, topic, module_title, user_level, context):
        prompt = (
            f"Teach a lesson on '{topic}' within the module '{module_title}'.\n"
            f"User Level: {user_level}\n"
            f"Context: {context}\n\n"
            "Structure:\n"
            "1. Introduction (Analogy/Hook)\n"
            "2. Core Concept Explanation\n"
            "3. Example / Real-world Use Case\n"
            "4. Code Snippet (if technical)\n"
            "5. Summary & Key Takeaways\n"
            "6. Checkpoint Question to test understanding."
        )
        return self.generate_response(prompt)

from app.agents.base_agent import BaseAgent

class AssessmentAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            role="Assessment & Evaluation Agent",
            system_instruction=(
                "You create assessments with MCQs, Short Answer, and Practical Tasks. "
                "You also evaluate answers, identify weak areas, and provide constructive feedback."
            )
        )

    def generate_quiz(self, module_title, key_concepts):
        prompt = (
            f"Generate a quiz for module '{module_title}'.\n"
            f"Concepts covered: {key_concepts}\n\n"
            "Format:\n"
            "1. 5 Multiple Choice Questions (with correct answers indicated)\n"
            "2. 2 Short Answer Questions\n"
            "3. 1 Practical Task description."
        )
        return self.generate_response(prompt)

    def evaluate_submission(self, quiz_content, user_answers):
        prompt = (
            f"Evaluate the following quiz submission:\n\n"
            f"Quiz Content: {quiz_content}\n"
            f"User Answers: {user_answers}\n\n"
            "Provide:\n"
            "1. Score (out of 100)\n"
            "2. Detailed Feedback per question\n"
            "3. Weak Areas detected\n"
            "4. Improvement Strategy."
        )
        return self.generate_response(prompt)

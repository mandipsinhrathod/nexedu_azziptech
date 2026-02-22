from app.agents.base_agent import BaseAgent

class AnalyticsAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            role="Learning Analytics Agent",
            system_instruction=(
                "You analyze user learning patterns, detect weak modules, suggest revisions, "
                "and recommend difficulty adjustments. You generate progress reports."
            )
        )

    def analyze_progress(self, user_history, scores):
        prompt = (
            f"Analyze the user's progress based on:\n"
            f"History: {user_history}\n"
            f"Scores: {scores}\n\n"
            "Identify:\n"
            "1. Completion %\n"
            "2. Weak Modules\n"
            "3. Suggested Revision approach\n"
            "4. Recommended difficulty adjustment (Increase/Decrease/Same)\n"
            "5. Generate a motivational summary."
        )
        return self.generate_response(prompt)

from app.services.llm_service import LLMService

class BaseAgent:
    def __init__(self, role, system_instruction):
        self.role = role
        self.system_instruction = system_instruction
        self.llm_service = LLMService()

    def generate_response(self, user_input):
        full_system_prompt = f"You are the {self.role}. {self.system_instruction}"
        return self.llm_service.generate_completion(user_input, full_system_prompt)

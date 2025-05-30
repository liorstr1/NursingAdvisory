from agents.llm_agents.fake_characters.fake_patient_character_1 import PATIENT_CHARACTER_1, PatientCharacterOutput1
from agents.llm_agents.llm_base_agent import LLMBaseAgent


class LLMFakeUserAgent(LLMBaseAgent):
    def __init__(self, user_charcter, user_output):
        super().__init__()
        super().update_agent_info(user_charcter)
        super().update_parser(user_output)
        self.update_prompts({})


if __name__ == "__main__":
    llm_fake_patient_agent = LLMFakeUserAgent(PATIENT_CHARACTER_1, PatientCharacterOutput1)
    chat_history = {}
    llm_fake_patient_agent.update_prompts(chat_history)
    response_anthropic = llm_fake_patient_agent.generate_response_from_anthropic()
    # response_openai = llm_fake_patient_agent.generate_response_from_openai()
    print(response_anthropic)
    # print(response_openai)

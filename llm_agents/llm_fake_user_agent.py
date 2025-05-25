from llm_agents.fake_characters.fake_user_character_1 import USER_CHARACTER_1, UserCharacterOutput1
from llm_agents.llm_base_agent import LLMBaseAgent


class LLMFakeUserAgent(LLMBaseAgent):
    def __init__(self, user_charcter, user_output):
        super().__init__()
        super().update_agent_info(user_charcter)
        super().update_parser(user_output)


if __name__ == "__main__":
    llm_fake_user_agent = LLMFakeUserAgent(USER_CHARACTER_1, UserCharacterOutput1)
    chat_history = {}
    response_anthropic = llm_fake_user_agent.generate_response_from_anthropic(chat_history)
    response_openai = llm_fake_user_agent.generate_response_from_openai(chat_history)

from agents.llm_agents.llm_base_agent import LLMBaseAgent


class LLMManagerAgent(LLMBaseAgent):
    def __init__(self, user_charcter, user_output):
        super().__init__()
        super().update_agent_info(user_charcter)
        super().update_parser(user_output)

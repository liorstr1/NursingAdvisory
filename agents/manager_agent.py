from agents.llm_agents.llm_manager_agent import LLMManagerAgent
from pubsub_utils.pubsub_functions import PubsubFunctions


class ManagerAgent(PubsubFunctions):
    def __init__(
            self,
            agent_name,
            agent_character,
            agent_permissions
    ):
        self.agent_name = agent_name
        super().__init__(agent_permissions, agent_name)
        self.llm_options = LLMManagerAgent(agent_character[0], agent_character[1])

    def publish_one_message(self, message, topic):
        pass

    def handle_incoming_message(self, message):
        pass

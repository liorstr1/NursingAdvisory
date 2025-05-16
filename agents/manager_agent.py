from entities import AgentType
from llm_agents.llm_manager_agent import LLMManagerAgent
from pubsub_utils.pubsub_functions import PubsubFunctions
from pubsub_utils.pubsub_permissions import TypeToPubsub


class MainManagerAgent(PubsubFunctions):
    def __init__(self, agent_name):
        self.agent_name = agent_name
        self.agent_type = AgentType.ADVISORY_MANAGER
        self.pubsub_permission = TypeToPubsub(agent_type=self.agent_type)
        super().__init__(self.pubsub_permission, agent_name)
        self.llm_capabilities = LLMManagerAgent()

    def publish_one_message(self, message, topic):
        pass

    def handle_incoming_message(self, message):
        pass

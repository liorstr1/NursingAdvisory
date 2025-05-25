from entities import USER
from llm_agents.all_fake_characters import ALL_FAKE_CHARACTERS
from llm_agents.fake_characters.fake_user_character_1 import USER_CHARACTER_1, UserCharacterOutput1
from llm_agents.llm_fake_user_agent import LLMFakeUserAgent
from pubsub_utils.pubsub_functions import PubsubFunctions
from pubsub_utils.pubsub_permissions import TypeToPubsub


class UserAgent(PubsubFunctions):
    def __init__(
            self,
            agent_name,
            agent_character,
            agent_permissions,
    ):
        super().__init__(agent_permissions, agent_name)
        self.llm_options = LLMFakeUserAgent(agent_character[0], agent_character[1])
        self.agent_name = agent_name

    def handle_incoming_message(self, message):
        print(f"TestAgent received message: {message}")

    def publish_one_message(self, message: str, topic: str):
        if self.sending_to and topic in self.sending_to:
            try:
                self.pubsub_service.publish_message(topic, message)
            except Exception as e:
                print(f"{self.agent_name} Failed to publish message: {message}", e)


if __name__ == "__main__":
    user_charater = ALL_FAKE_CHARACTERS["users"][0]
    user_agent_1 = UserAgent("user_1", user_charater, USER)
    print(user_agent_1)

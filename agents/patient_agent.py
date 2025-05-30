from entities import PATIENT
from agents.llm_agents.all_characters_list import ALL_CHARACTERS
from agents.llm_agents.llm_fake_patient_agent import LLMFakeUserAgent
from pubsub_utils.pubsub_functions import PubsubFunctions


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
                print(f"{self.agent_name} Publishing to topic: {topic}, message: {message[:20]}")
                self.pubsub_service.publish_message(topic, message)
            except Exception as e:
                print(f"{self.agent_name} Failed to publish message: {message}", e)

    @staticmethod
    def get_one_patient_data(patinet_idx):
        return ALL_CHARACTERS[PATIENT][patinet_idx]


if __name__ == "__main__":
    patient_charater = ALL_CHARACTERS[PATIENT][0]
    patient_agent_1 = UserAgent("patient_1", patient_charater, PATIENT)
    print(patient_agent_1)

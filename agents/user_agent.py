from NursingAdvisory.main_functions.pubsub_functions import PubsubFunctions


class TestAgent(PubsubFunctions):
    def __init__(
            self,
            listen_incoming_topic,
            agent_name="test_agent"
    ):
        super().__init__(listen_incoming_topic, agent_name)

    def handle_incoming_message(self, message):
        print(f"TestAgent received message: {message}")

    def publish_one_message(self, message, topic):
        if self.send_list and topic in self.send_list:
            try:
                self.pubsub_service.publish_message(topic, message)
            except Exception as e:
                print(f"{self.agent_name} Failed to publish message: {message}", e)

import os
from abc import ABC, abstractmethod
from services.pubsub_service import PubSubService
from services.secret_manager_service import SecretManagerService
from dotenv import load_dotenv

from helper_methods import get_pubsub_postfix

load_dotenv()


class PubsubFunctions(ABC):
    def __init__(self, agent_name, incoming_topics, outgoing_topics):
        self.pubsub_postfix = get_pubsub_postfix()
        self.agent_name = agent_name
        self.pubsub_service = PubSubService('botit1')
        self.secret_manager = SecretManagerService('botit1')
        self.listen_to = []
        self.sending_to = []

        for listen_topic in incoming_topics:
            current_topic = f"{listen_topic}{self.pubsub_postfix}"
            self.pubsub_service.subscribe_to_topic(
                topic_name=f"{current_topic}",
                subscription_name=f"{current_topic}_subscription",
                message_handler=self.handle_incoming_message
            )
            self.listen_to.append(f"{current_topic}")

        for outgoing_topic in outgoing_topics:
            current_topic = f"{outgoing_topic}{self.pubsub_postfix}"
            self.sending_to.append(current_topic)

    @abstractmethod
    def handle_incoming_message(self, message):
        pass

    @abstractmethod
    def publish_one_message(self, message, topic):
        pass

    def check_if_listen_to(self, pub_sub_topic):
        return self.listen_to


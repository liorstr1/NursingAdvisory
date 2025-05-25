from abc import ABC, abstractmethod
from pubsub_utils.pubsub_service import PubSubService
from services.secret_manager_service import SecretManagerService
from dotenv import load_dotenv
from helper_methods import get_pubsub_postfix
from pubsub_utils.pubsub_permissions import TypeToPubsub
load_dotenv()


class PubsubFunctions(ABC):
    def __init__(self, agent_permissions: str, agent_name: str = ""):
        self.sending_to = []
        self.listen_to = []
        self.pubsub_postfix = get_pubsub_postfix()
        self.pubsub_service = PubSubService('botit1')
        self.secret_manager = SecretManagerService('botit1')

        type_to_sub = TypeToPubsub(agent_permissions)
        for listen_topic in type_to_sub.listen_to:
            print(f"{agent_name} subscribing to {listen_topic}")
            current_topic = f"{listen_topic}_{self.pubsub_postfix}"
            self.pubsub_service.subscribe_to_topic(
                topic_name=f"{current_topic}",
                subscription_name=f"{current_topic}_subscription",
                message_handler=self.handle_incoming_message
            )
            self.listen_to.append(f"{current_topic}")

        for outgoing_topic in type_to_sub.sending_to:
            current_topic = f"{outgoing_topic}_{self.pubsub_postfix}"
            self.sending_to.append(current_topic)

    @abstractmethod
    def handle_incoming_message(self, message):
        pass

    @abstractmethod
    def publish_one_message(self, message, topic):
        pass

    def check_if_listen_to(self, pub_sub_topic):
        return self.listen_to


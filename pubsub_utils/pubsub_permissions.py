from entities import (
    ADVISORY_MANAGER, FROM_USERS_PUBSUB, TO_USERS_PUBSUB, FROM_STAFF_PUBSUB, TO_STAFF_PUBSUB
)

TYPE_TO_PERMISSIONS = {
    ADVISORY_MANAGER: [[FROM_USERS_PUBSUB, FROM_STAFF_PUBSUB],[TO_USERS_PUBSUB, TO_STAFF_PUBSUB]]
}


class TypeToPubsub:
    def __init__(self, agent_type):
        self.agent_type = agent_type
        if agent_type not in TYPE_TO_PERMISSIONS:
            raise Exception(f"Type {agent_type} not found in TYPE_TO_PERMISSIONS")
        self.listen_to = TYPE_TO_PERMISSIONS.get(agent_type[0], [])
        self.sending_to = TYPE_TO_PERMISSIONS.get(agent_type[1], [])

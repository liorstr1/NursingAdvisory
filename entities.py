from enum import Enum
PROJECT_NAME = "NursingAdvisory"
NURSING_ADVISORY_COLLECTION_NAME = "nursing_advisory_data"
LOCAL = "local"
DEV = "dev"
PROD = "prod"

ADVISORY_MANAGER = "advisory_manager"

# pub sub entities
# incoming pubsubs
FROM_USERS_PUBSUB = "from_users"
FROM_STAFF_PUBSUB = "from_staff"

# outgoing pubsubs
TO_USERS_PUBSUB = "to_users"
TO_STAFF_PUBSUB = "to_staff"

MAIN_ADVISORY_PUBSUB_PREFIX = "main_advisory"
ADVISORY_TOPIC_NAME = "advisory_topic"
ADVISORY_SUBSCRIPTION_NAME = "advisory_subscription"


class AgentType(Enum):
    ADVISORY_MANAGER = "advisory_manager"

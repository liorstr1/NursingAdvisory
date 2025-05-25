from enum import Enum
PROJECT_NAME = "NursingAdvisory"
NURSING_ADVISORY_COLLECTION_NAME = "nursing_advisory_data"
LOCAL = "local"
DEV = "dev"
PROD = "prod"
DEFAULT_CLAUDE_MODEL = "claude-3-5-sonnet-latest"

USER_TO_MANAGER = "user_to_manager"
MANAGER_TO_USER = "manager_to_user"
MANAGER_TO_STAFF = "manager_to_staff"
STAFF_TO_MANAGER = "staff_to_manager"


ADVISORY_MANAGER = "advisory_manager"
USER = "user"
MAIN_ADVISORY_PUBSUB_PREFIX = "main_advisory"
ADVISORY_TOPIC_NAME = "advisory_topic"
ADVISORY_SUBSCRIPTION_NAME = "advisory_subscription"


class AgentType(Enum):
    ADVISORY_MANAGER = "advisory_manager"

from entities import (
    PATIENT_TO_MANAGER, MANAGER, STAFF_TO_MANAGER, MANAGER_TO_PATINET, MANAGER_TO_STAFF, PATIENT
)

TYPE_TO_PERMISSIONS = {
    MANAGER: [[PATIENT_TO_MANAGER, STAFF_TO_MANAGER], [MANAGER_TO_PATINET, MANAGER_TO_STAFF]],
    PATIENT: [[MANAGER_TO_PATINET], [PATIENT_TO_MANAGER]]
}


class TypeToPubsub:
    def __init__(self, agent_type):
        self.agent_type = agent_type
        if agent_type not in TYPE_TO_PERMISSIONS:
            raise Exception(f"Type {agent_type} not found in TYPE_TO_PERMISSIONS")
        self.listen_to = TYPE_TO_PERMISSIONS[agent_type][0]
        self.sending_to = TYPE_TO_PERMISSIONS[agent_type][1]

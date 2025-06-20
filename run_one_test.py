import json
import time
from agents.patient_agent import UserAgent
from all_classes.manager_class import ManagerAgent
from entities import PATIENT, PATIENT_TO_MANAGER


def test_active_one_session(active_manager: ManagerAgent):
    patient_charater = UserAgent.get_one_patient_data(0)
    patient_agent_1 = UserAgent("patient_1", patient_charater, PATIENT)
    print("activated", patient_agent_1.agent_name)

    init_patient_message = {
        "message": patient_agent_1.llm_options.generate_response_from_anthropic(),
        "user_id": patient_charater[2]
    }

    patient_agent_1.publish_one_message(
        init_patient_message,
        f"{PATIENT_TO_MANAGER}{patient_agent_1.pubsub_postfix}"
    )
    while True:
        print("waiting for message")
        time.sleep(2)


from agents.llm_agents.fake_characters.fake_patient_character_1 import PATIENT_CHARACTER_1, PatientCharacterOutput1
from agents.llm_agents.fake_characters.manager_character_1 import MANAGER_CHARACTER_1, ManagerOutput
from entities import PATIENT, MANAGER

ALL_CHARACTERS = {
    PATIENT: [
        [PATIENT_CHARACTER_1, PatientCharacterOutput1],
    ],
    MANAGER: [
        [MANAGER_CHARACTER_1, ManagerOutput]
    ]
}

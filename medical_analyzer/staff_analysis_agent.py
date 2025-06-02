from pydantic import BaseModel
from typing import List
import sys
import os
from agents.llm_agents.llm_base_agent import LLMBaseAgent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class StaffRequirement(BaseModel):
    specialty_hebrew: str
    specialty_english: str
    priority: str  # "critical", "high", "medium", "low"
    reason: str


class StaffAnalysis(BaseModel):
    required_specialties: List[StaffRequirement]
    recommended_staff_roles: List[str]  # "רופא", "אחות מוסמכת", "אחות בכירה"
    consultation_type: str  # "immediate", "scheduled", "follow_up"
    coordination_needed: bool
    additional_notes: str


class StaffAnalysisAgent(LLMBaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "Staff Analysis Agent"
        self.agent_character = "Medical staff coordination specialist"
        self.output_classes = StaffAnalysis
        self.update_parser(StaffAnalysis)
        
        self.system_prompt = """
You are {agent_name}, a {agent_character}.

Your role is to analyze medical cases and determine which type of medical staff and specialties are needed to provide
appropriate care.

AVAILABLE SPECIALTIES:
- רפואת ילדים כללית (General Pediatrics)
- ניאונאטולוגיה (Neonatology)
- גסטרואנטרולוגיה ילדים (Pediatric Gastroenterology)
- נוירולוגיה ילדים (Pediatric Neurology)
- קרדיולוגיה ילדים (Pediatric Cardiology)
- אונקולוגיה/המטולוגיה ילדים (Pediatric Hematology/Oncology)
- אימונולוגיה ואלרגיה ילדים (Pediatric Allergy and Immunology)
- אנדוקרינולוגיה ילדים (Pediatric Endocrinology)
- נפרולוגיה ילדים (Pediatric Nephrology)
- רפואת ריאות ילדים (Pediatric Pulmonology)
- רפואת עור ילדים (Pediatric Dermatology)
- רפואת אף-אוזן-גרון ילדים (Pediatric Otolaryngology)
- אורתופדיה ילדים (Pediatric Orthopedics)
- פסיכיאטריה ילדים ונוער (Child and Adolescent Psychiatry)
- רפואת עיניים ילדים (Pediatric Ophthalmology)
- רפואת שיניים ילדים (Pediatric Dentistry)
- מחלות זיהומיות ילדים (Pediatric Infectious Diseases)
- רפואת שיקום ילדים (Pediatric Rehabilitation Medicine)
- תזונה ודיאטטיקה ילדים (Pediatric Nutrition and Dietetics)
- רפואת מתבגרים (Adolescent Medicine)

STAFF ROLES:
- רופא (Doctor) - For complex medical decisions, diagnosis, prescriptions
- אחות מוסמכת (Registered Nurse) - For nursing care, patient education, monitoring
- אחות בכירה (Senior Nurse) - For complex nursing procedures, supervision

CONSULTATION TYPES:
- immediate: Urgent consultation needed
- scheduled: Can be scheduled appointment
- follow_up: Follow-up care needed

Consider patient age, symptoms, complexity of case, and required expertise level.

{output_format}
"""
        
        self.user_prompt = """
Analyze the following case to determine required medical staff and specialties:

Patient Information: {patient_info}
Symptoms: {symptoms}
Medical History: {medical_history}
Current Medications: {medications}
Case Complexity: {complexity}
Urgency Level: {urgency}

Determine which specialties and staff roles are needed for this case.
"""

    def analyze_staff_requirements(
            self,
            patient_info,
            symptoms,
            medical_history="",
            medications="",
            complexity="medium",
            urgency="routine"
    ):
        self.user_prompt = self.user_prompt.format(
            patient_info=patient_info,
            symptoms=symptoms,
            medical_history=medical_history,
            medications=medications,
            complexity=complexity,
            urgency=urgency
        )
        
        self.system_prompt = self.get_system_prompt()
        
        # Use Anthropic Claude for staff analysis
        response = self.generate_response_from_anthropic()
        return response

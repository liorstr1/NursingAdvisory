from pydantic import BaseModel
from typing import List
import sys
import os
from agents.llm_agents.llm_base_agent import LLMBaseAgent

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MissingDetail(BaseModel):
    detail_category: str  # "symptoms", "medical_history", "medications", "allergies", "vital_signs", "family_history"
    specific_question: str
    importance: str  # "critical", "high", "medium", "low"
    reason: str


class ProvidedDetail(BaseModel):
    category: str
    information: str
    completeness: str  # "complete", "partial", "insufficient"


class MedicalDetailsAnalysis(BaseModel):
    provided_details: List[ProvidedDetail]
    missing_details: List[MissingDetail]
    information_completeness_score: int  # 1-10 scale
    recommended_questions: List[str]
    next_assessment_steps: List[str]
    case_clarity: str  # "clear", "needs_clarification", "insufficient_data"


class MedicalDetailsAgent(LLMBaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "Medical Details Agent"
        self.agent_character = "Medical information assessment specialist"
        self.output_classes = MedicalDetailsAnalysis
        self.update_parser(MedicalDetailsAnalysis)

        self.system_prompt = """
You are {agent_name}, a {agent_character}.

Your role is to analyze what medical information has been provided and identify what additional details are needed
for proper assessment and care planning.

MEDICAL INFORMATION CATEGORIES:
1. Current Symptoms:
   - Onset, duration, severity, location
   - Aggravating/relieving factors
   - Associated symptoms

2. Medical History:
   - Previous illnesses, surgeries, hospitalizations
   - Chronic conditions
   - Previous similar episodes

3. Medications:
   - Current medications and dosages
   - Recent medication changes
   - Medication allergies or adverse reactions

4. Allergies:
   - Drug allergies
   - Food allergies
   - Environmental allergies

5. Vital Signs:
   - Temperature, pulse, blood pressure
   - Respiratory rate, oxygen saturation
   - Weight, height (for pediatric cases)

6. Family History:
   - Genetic conditions
   - Relevant family medical history

7. Social History:
   - Recent travel, exposures
   - School/daycare attendance
   - Vaccination status

8. Physical Examination Findings:
   - Appearance, behavior
   - System-specific findings

For pediatric cases, also consider:
- Feeding patterns (for infants)
- Developmental milestones
- Growth patterns
- Immunization history

Rate information completeness on 1-10 scale:
1-3: Insufficient for assessment
4-6: Basic information, needs significant details
7-8: Good information, minor gaps
9-10: Comprehensive information

{output_format}
"""

        self.user_prompt = """
Analyze the provided medical information and identify gaps:

Patient Information: {patient_info}
Chief Complaint: {chief_complaint}
Symptoms Provided: {symptoms}
Medical History Provided: {medical_history}
Medications Provided: {medications}
Allergies Provided: {allergies}
Vital Signs Provided: {vital_signs}
Physical Exam Findings: {physical_exam}
Additional Information: {additional_info}

Assess what information is complete, what is missing, and what questions should be asked next.
"""

    def analyze_medical_details(self, patient_info, chief_complaint, symptoms="", medical_history="",
                                medications="", allergies="", vital_signs="", physical_exam="", additional_info=""):
        self.user_prompt = self.user_prompt.format(
            patient_info=patient_info,
            chief_complaint=chief_complaint,
            symptoms=symptoms,
            medical_history=medical_history,
            medications=medications,
            allergies=allergies,
            vital_signs=vital_signs,
            physical_exam=physical_exam,
            additional_info=additional_info
        )

        self.system_prompt = self.get_system_prompt()

        # Use Anthropic Claude for medical details analysis
        response = self.generate_response_from_anthropic()
        return response

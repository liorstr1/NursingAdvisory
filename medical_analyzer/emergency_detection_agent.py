from pydantic import BaseModel
import sys
import os
from agents.llm_agents.llm_base_agent import LLMBaseAgent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class EmergencyAnalysis(BaseModel):
    is_emergency: bool
    emergency_level: str  # "none", "low", "moderate", "high", "critical"
    emergency_reason: str
    recommended_action: str
    time_sensitivity: str  # "immediate", "urgent", "soon", "routine"


class EmergencyDetectionAgent(LLMBaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "Emergency Detection Agent"
        self.agent_character = "Medical emergency assessment specialist"
        self.output_classes = EmergencyAnalysis
        self.update_parser(EmergencyAnalysis)
        
        self.system_prompt = """
You are {agent_name}, a {agent_character}.

Your role is to analyze medical cases and determine if they require emergency treatment outside the
scope of nursing advisory services.

CRITICAL EMERGENCY INDICATORS:
- Severe chest pain, difficulty breathing, loss of consciousness
- Severe bleeding, trauma, burns
- Signs of stroke (FAST protocol), heart attack symptoms
- Severe allergic reactions, anaphylaxis
- High fever with altered mental status
- Severe abdominal pain with vomiting
- Poisoning or overdose
- Severe dehydration in vulnerable populations
- Any life-threatening symptoms

NURSING ADVISORY SCOPE (NOT EMERGENCY):
- Minor wounds, bruises, sprains
- Common cold, mild fever
- Medication questions and adherence
- Routine health monitoring
- Preventive care guidance
- Chronic disease management advice
- Minor skin conditions

For emergency cases, recommend "RUN TO THE HOSPITAL IMMEDIATELY"
For non-emergency cases, indicate they can proceed with nursing advisory.

{output_format}
"""
        
        self.user_prompt = """
Analyze the following medical case for emergency status:

Patient Information: {patient_info}
Symptoms: {symptoms}
Duration: {duration}
Severity: {severity}
Additional Context: {additional_context}

Determine if this requires immediate emergency care or can be handled through nursing advisory.
"""

    def analyze_emergency_status(self, patient_info, symptoms, duration="", severity="", additional_context=""):
        self.user_prompt = self.user_prompt.format(
            patient_info=patient_info,
            symptoms=symptoms,
            duration=duration,
            severity=severity,
            additional_context=additional_context
        )
        
        self.system_prompt = self.get_system_prompt()
        
        # Use Anthropic Claude for emergency detection
        response = self.generate_response_from_anthropic()
        return response

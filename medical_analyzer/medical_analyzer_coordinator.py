import sys
import os
from medical_analyzer.emergency_detection_agent import EmergencyDetectionAgent
from medical_analyzer.staff_analysis_agent import StaffAnalysisAgent
from medical_analyzer.medical_details_agent import MedicalDetailsAgent

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MedicalAnalyzerCoordinator:
    def __init__(self):
        self.emergency_agent = EmergencyDetectionAgent()
        self.staff_agent = StaffAnalysisAgent()
        self.details_agent = MedicalDetailsAgent()

    def analyze_medical_case(self, patient_info, chief_complaint, symptoms="", medical_history="",
                             medications="", allergies="", vital_signs="", physical_exam="",
                             additional_info="", severity="", duration=""):
        """
        Comprehensive medical case analysis that returns emergency status, 
        staff requirements, and medical details assessment.
        """

        # 1. Emergency Detection Analysis
        emergency_analysis = self.emergency_agent.analyze_emergency_status(
            patient_info=patient_info,
            symptoms=symptoms,
            duration=duration,
            severity=severity,
            additional_context=f"Chief complaint: {chief_complaint}. Additional info: {additional_info}"
        )

        # 2. Staff Analysis (only if not emergency)
        staff_analysis = None
        if not (emergency_analysis and emergency_analysis.is_emergency):
            staff_analysis = self.staff_agent.analyze_staff_requirements(
                patient_info=patient_info,
                symptoms=symptoms,
                medical_history=medical_history,
                medications=medications,
                complexity="medium",  # Can be parameterized
                urgency="routine" if not emergency_analysis else "urgent"
            )

        # 3. Medical Details Analysis
        details_analysis = self.details_agent.analyze_medical_details(
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

        return {
            "emergency_analysis": emergency_analysis,
            "staff_analysis": staff_analysis,
            "details_analysis": details_analysis,
            "session_guidance": self._generate_session_guidance(
                emergency_analysis, staff_analysis, details_analysis
            )
        }

    @staticmethod
    def _generate_session_guidance(emergency_analysis, staff_analysis, details_analysis):
        """
        Generate guidance for the active session based on all analyses.
        """
        guidance = {
            "immediate_actions": [],
            "required_staff": [],
            "questions_to_ask": [],
            "next_steps": [],
            "alert_level": "normal"
        }

        # Emergency handling
        if emergency_analysis and emergency_analysis.is_emergency:
            guidance["immediate_actions"].append("EMERGENCY ALERT: RUN TO THE HOSPITAL IMMEDIATELY")
            guidance["alert_level"] = "emergency"
            guidance["next_steps"].append("Direct patient to emergency care")
            return guidance

        # Staff requirements
        if staff_analysis:
            for specialty in staff_analysis.required_specialties:
                guidance["required_staff"].append({
                    "specialty": specialty.specialty_english,
                    "priority": specialty.priority,
                    "reason": specialty.reason
                })

        # Information gaps
        if details_analysis:
            for missing_detail in details_analysis.missing_details:
                if missing_detail.importance in ["critical", "high"]:
                    guidance["questions_to_ask"].append(missing_detail.specific_question)

            guidance["next_steps"].extend(details_analysis.next_assessment_steps)

        return guidance

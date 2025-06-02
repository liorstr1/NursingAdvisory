import threading
from talk_to_mongo import MongoConnection
from medical_analyzer import MedicalAnalyzerCoordinator


class ActiveSession:
    def __init__(
            self,
            session_id: str,
            user_id: str
    ):
        self.session_id = session_id
        self.user_id = user_id
        self._lock = threading.Lock()
        self.mongo_connection = MongoConnection()
        self.medical_analyzer = MedicalAnalyzerCoordinator()
        self.medical_analysis_results = None
        self.session_guidance = None
        print(f"user: {user_id} activated new session")
        self.mongo_connection.create_new_session(session_id, user_id)

    def analyze_medical_case(self, patient_info, chief_complaint, symptoms="", medical_history="",
                             medications="", allergies="", vital_signs="", physical_exam="",
                             additional_info="", severity="", duration=""):
        """
        Perform comprehensive medical case analysis and update session guidance.
        """
        with self._lock:
            self.medical_analysis_results = self.medical_analyzer.analyze_medical_case(
                patient_info=patient_info,
                chief_complaint=chief_complaint,
                symptoms=symptoms,
                medical_history=medical_history,
                medications=medications,
                allergies=allergies,
                vital_signs=vital_signs,
                physical_exam=physical_exam,
                additional_info=additional_info,
                severity=severity,
                duration=duration
            )

            self.session_guidance = self.medical_analysis_results["session_guidance"]

            # Store analysis results in MongoDB
            self.mongo_connection.store_medical_analysis(
                self.session_id,
                self.medical_analysis_results
            )

            return self.medical_analysis_results

    def get_emergency_status(self):
        """
        Check if this case requires emergency care.
        """
        if not self.medical_analysis_results:
            return None

        emergency_analysis = self.medical_analysis_results.get("emergency_analysis")
        if emergency_analysis and emergency_analysis.is_emergency:
            return {
                "is_emergency": True,
                "alert_message": "RUN TO THE HOSPITAL IMMEDIATELY",
                "emergency_level": emergency_analysis.emergency_level,
                "reason": emergency_analysis.emergency_reason
            }

        return {"is_emergency": False}

    def get_required_staff(self):
        """
        Get the list of required medical staff for this case.
        """
        if not self.session_guidance:
            return []

        return self.session_guidance.get("required_staff", [])

    def get_questions_to_ask(self):
        """
        Get the list of questions that should be asked to gather missing medical information.
        """
        if not self.session_guidance:
            return []

        return self.session_guidance.get("questions_to_ask", [])

    def get_next_steps(self):
        """
        Get the recommended next steps for this medical case.
        """
        if not self.session_guidance:
            return []

        return self.session_guidance.get("next_steps", [])

    def is_emergency_case(self):
        """
        Quick check if this is an emergency case.
        """
        emergency_status = self.get_emergency_status()
        return emergency_status and emergency_status.get("is_emergency", False)

    def cleanup(self):
        pass

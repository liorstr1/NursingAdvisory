import asyncio
import hashlib
import threading
import time
from agents.llm_agents.llm_manager_agent import LLMManagerAgent
from all_classes.active_session_class import ActiveSession
from services.pubsub_functions import PubsubFunctions


class ManagerAgent(PubsubFunctions):
    def __init__(
            self,
            agent_name,
            agent_character,
            agent_permissions
    ):
        self._lock = threading.Lock()
        self.running = False
        self.listener_thread = None
        self.initialized = False
        self.init_callback = None
        self.init_event = threading.Event()

        self.active_sessions: dict[str, ActiveSession] = {}
        self._lock = threading.Lock()
        self._running = False
        print("Manager Agent initialized")
        self.agent_name = agent_name

        super().__init__(agent_permissions, agent_name)
        self.llm_options = LLMManagerAgent(agent_character[0], agent_character[1])

    def set_init_callback(self, callback):
        self.init_callback = callback
        if self.initialized:
            self.init_callback()

    def initialize(self):
        self.initialized = True
        self.init_event.set()
        if self.init_callback:
            self.init_callback()

    def start_in_background(self):
        self.running = True
        self.listener_thread = threading.Thread(target=self.start, daemon=True)
        self.listener_thread.start()
        return self.listener_thread

    def cleanup(self):
        self.running = False

    async def wait_for_initialization(self, timeout=5.0):
        if self.initialized:
            return True
        start_time = time.time()
        while not self.initialized and time.time() - start_time < timeout:
            await asyncio.sleep(0.1)
        return self.initialized

    def stop(self):
        self.running = False
        if hasattr(self, 'pubsub_service'):
            self.pubsub_service.close()
        if hasattr(self, 'listener_thread') and self.listener_thread and self.listener_thread.is_alive():
            self.listener_thread.join(timeout=2)

    def start(self):
        self.running = True
        try:
            self.initialize()
            while self.running:
                time.sleep(1)

        except KeyboardInterrupt:
            print("\nShutting down gracefully...")
        except Exception as e:
            print(f"Error in message listener: {str(e)}")
        finally:
            if hasattr(self, 'pubsub_service'):
                self.pubsub_service.close()
            self.running = False

    def publish_one_message(self, message, topic):
        pass

    def get_or_create_session(self, user_id: str) -> ActiveSession:
        """Get existing session or create new one for hashed user_id"""
        hashed_user_id = hashlib.sha256(user_id.encode()).hexdigest()
        
        with self._lock:
            if hashed_user_id in self.active_sessions:
                return self.active_sessions[hashed_user_id]
            else:
                # Create new session with hashed user_id as session_id
                new_session = ActiveSession(hashed_user_id, user_id)
                self.active_sessions[hashed_user_id] = new_session
                print(f"Created new session for user {user_id} with hash {hashed_user_id[:8]}...")
                return new_session

    def handle_incoming_message(self, message):
        print(f"ManagerAgent received message: {message}")
        if hasattr(message, 'user_id') or (isinstance(message, dict) and 'user_id' in message):
            user_id = message.user_id if hasattr(message, 'user_id') else message['user_id']
            session = self.get_or_create_session(user_id)
            print(f"Message routed to session: {session.session_id[:8]}...")
            
            # Trigger medical analysis if this is a new medical case
            if self._is_medical_case_message(message):
                self._process_medical_case(session, message)
                
        else:
            print("Warning: Message does not contain user_id")
    
    @staticmethod
    def _is_medical_case_message(message):
        """Check if message contains medical case information that needs analysis"""
        if isinstance(message, dict):
            medical_keywords = ['symptoms', 'chief_complaint', 'medical_history', 'pain', 'fever', 'illness']
            message_text = str(message).lower()
            return any(keyword in message_text for keyword in medical_keywords)
        return False
    
    def _process_medical_case(self, session: ActiveSession, message):
        """Process medical case through the medical analyzer"""
        try:
            # Extract medical information from message
            patient_info = self._extract_patient_info(message)
            chief_complaint = self._extract_chief_complaint(message)
            symptoms = self._extract_symptoms(message)
            
            # Run medical analysis
            analysis_results = session.analyze_medical_case(
                patient_info=patient_info,
                chief_complaint=chief_complaint,
                symptoms=symptoms
            )
            
            # Check for emergency
            if session.is_emergency_case():
                emergency_status = session.get_emergency_status()
                print(f"🚨 EMERGENCY DETECTED: {emergency_status['alert_message']}")
                # Send emergency alert to patient immediately
                self._send_emergency_alert(session, emergency_status)
            else:
                # Process non-emergency case
                required_staff = session.get_required_staff()
                questions = session.get_questions_to_ask()
                print(f"Required staff: {required_staff}")
                print(f"Questions to ask: {questions}")
                
        except Exception as e:
            print(f"Error processing medical case: {e}")
    
    def _extract_patient_info(self, message):
        """Extract patient information from message"""
        # This would parse the message to extract patient details
        return str(message.get('patient_info', '')) if isinstance(message, dict) else str(message)
    
    def _extract_chief_complaint(self, message):
        """Extract chief complaint from message"""
        return str(message.get('chief_complaint', '')) if isinstance(message, dict) else str(message)
    
    def _extract_symptoms(self, message):
        """Extract symptoms from message"""
        return str(message.get('symptoms', '')) if isinstance(message, dict) else str(message)
    
    def _send_emergency_alert(self, session: ActiveSession, emergency_status):
        """Send immediate emergency alert to patient"""
        alert_message = {
            "type": "emergency_alert",
            "message": emergency_status['alert_message'],
            "emergency_level": emergency_status['emergency_level'],
            "reason": emergency_status['reason'],
            "session_id": session.session_id
        }
        # Publish emergency alert to patient topic
        self.publish_one_message(alert_message, "to_users")

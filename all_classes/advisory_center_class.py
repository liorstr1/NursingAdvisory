import threading
import time
import asyncio
from dotenv import load_dotenv

from agents.llm_agents.all_characters_list import ALL_CHARACTERS
from agents.manager_agent import ManagerAgent
from all_classes.active_session_class import ActiveSession
from entities import MANAGER

load_dotenv()


class AdvisoryCenter:
    def __init__(self):
        self._lock = threading.Lock()
        self.running = False
        self.listener_thread = None
        self.initialized = False
        self.init_callback = None
        self.init_event = threading.Event()

        self.active_sessions: dict[str, ActiveSession] = {}
        self._lock = threading.Lock()
        self._running = False

        manager_charater = ALL_CHARACTERS[MANAGER][0]
        self.advisory_manager = ManagerAgent("manager_1", manager_charater, MANAGER)
        print("Advisory Center initialized")

    def set_init_callback(self, callback):
        self.init_callback = callback
        if self.initialized:
            self.init_callback()

    def initialize(self):
        self.initialized = True
        self.init_event.set()
        if self.init_callback:
            self.init_callback()

    @staticmethod
    def handle_message(message):
        """Handle incoming message from PubSub"""
        try:
            client_id = message["client_id"]
            print(f"[AdvisoryCenter] Processing message for client {client_id}")
            # process new message

        except Exception as e:
            print(f"[AdvisoryCenter] Failed to handle message: {message}", e)

    def cleanup(self):
        self.running = False

    def start_in_background(self):
        self.running = True
        self.listener_thread = threading.Thread(target=self.start, daemon=True)
        self.listener_thread.start()
        return self.listener_thread

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

import os
import threading
import time
import asyncio
from dotenv import load_dotenv
from pymongo import MongoClient

from entities import MAIN_ADVISORY_PUBSUB_PREFIX
from pubsub_service import PubSubService
from running_one_session import ActiveSession
from secret_manager_service import SecretManagerService
load_dotenv()


class AdvisoryCenter:
    def __init__(self, database=os.environ.get("LOCAL_DB")):
        self.mongo_client = MongoClient(os.environ.get("MONGO_CLIENT"))
        self.db = self.mongo_client[database]
        self.pubsub_service = PubSubService('botit1')
        self.secret_manager = SecretManagerService('botit1')
        self._lock = threading.Lock()
        self.running = False
        self.listener_thread = None
        self.initialized = False
        self.init_callback = None
        self.init_event = threading.Event()

        self.active_sessions: dict[str, ActiveSession] = {}
        self._lock = threading.Lock()
        self._running = False
        print("Advisory Center initialized")

    def set_init_callback(self, callback):
        self.init_callback = callback
        if self.initialized:
            self.init_callback()

    def initialize(self):
        topic_name = f'incoming_messages{MAIN_ADVISORY_PUBSUB_PREFIX}'
        subscription_name = f'incoming_messages{MAIN_ADVISORY_PUBSUB_PREFIX}_sub'
        self.pubsub_service.check_or_create_topic(topic_name)
        self.pubsub_service.check_or_create_subscription(topic_name, subscription_name)

        self.pubsub_service.subscribe_to_topic(
            topic_name=topic_name,
            subscription_name=subscription_name,
            message_handler=self.handle_message
        )

        print(f"MessageListener initialized and subscribed to {topic_name}")
        self.initialized = True
        self.init_event.set()
        if self.init_callback:
            self.init_callback()

    def handle_message(self, message):
        """Handle incoming message from PubSub"""
        try:
            client_id = message["client_id"]
            print(f"[AdvisoryCenter] Processing message for client {client_id}")
            # process new message

        except Exception as e:
            print(f"[AdvisoryCenter] Failed to handle message: {message}", e)

    def cleanup(self):
        self.running = False
        if self.mongo_client:
            self.mongo_client.close()

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

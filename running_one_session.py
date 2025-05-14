import threading
from talk_to_mongo import MongoConnection


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
        print(f"user: {user_id} activated new session")
        self.mongo_connection.create_new_session(session_id, user_id)

    def cleanup(self):
        pass

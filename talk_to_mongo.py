import os
from pymongo import MongoClient
from dotenv import load_dotenv
from entities import NURSING_ADVISORY_COLLECTION_NAME
from helper_methods import get_time_in_epoc

load_dotenv()


class MongoConnection:
    def __init__(self):
        mongo_uri = os.getenv("LOCAL_MONGO_CLIENT")
        db_name = os.getenv("LOCAL_DB")
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db[NURSING_ADVISORY_COLLECTION_NAME]

    def get_collection(self):
        return self.collection

    def close(self):
        self.client.close()

    def create_new_session(self, session_id, user_id):
        self.collection.insert_one({
            "session_id": session_id,
            "user_id": user_id,
            "session_start_time": get_time_in_epoc(),
            "messages": [],
            "all_decisions": [],
            "staff_ids": [],
            "session_status": "init",
            "medical_analysis": None
        })

    def store_medical_analysis(self, session_id, analysis_results):
        """
        Store medical analysis results in the session document.
        """
        self.collection.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "medical_analysis": {
                        "emergency_analysis": analysis_results.get("emergency_analysis").__dict__ if analysis_results.get("emergency_analysis") else None,
                        "staff_analysis": analysis_results.get("staff_analysis").__dict__ if analysis_results.get("staff_analysis") else None,
                        "details_analysis": analysis_results.get("details_analysis").__dict__ if analysis_results.get("details_analysis") else None,
                        "session_guidance": analysis_results.get("session_guidance"),
                        "analysis_timestamp": get_time_in_epoc()
                    }
                }
            }
        )

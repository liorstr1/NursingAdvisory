from pymongo import MongoClient
from datetime import datetime
import pytz


def get_available_staff_by_specialty(db, specialty_name):
    israel_tz = pytz.timezone("Asia/Jerusalem")
    now = datetime.now(israel_tz)
    current_day = now.strftime('%A')
    current_hour = now.hour
    day_map = {
        "Sunday": "ראשון",
        "Monday": "שני",
        "Tuesday": "שלישי",
        "Wednesday": "רביעי",
        "Thursday": "חמישי",
        "Friday": "שישי",
        "Saturday": "שבת"
    }
    hebrew_day = day_map[current_day]
    query = {
        "$or": [
            {"specialties_english": specialty_name},
            {"specialties_hebrew": specialty_name}
        ],
        f"availability.{hebrew_day}": {"$exists": True}
    }

    available_ids = []
    for doc in db.find(query, {"id": 1, "availability": 1}):
        time_ranges = doc["availability"].get(hebrew_day, [])
        for tr in time_ranges:
            start_str, end_str = tr.split("-")
            start_hour = int(start_str.split(":")[0])
            end_hour = int(end_str.split(":")[0])
            if start_hour <= current_hour < end_hour:
                available_ids.append(doc["id"])
                break

    return available_ids


def get_time_in_epoc():
    import datetime
    current_time = datetime.datetime.now()
    return int(current_time.timestamp() * 1000)
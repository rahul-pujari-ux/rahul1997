import json
from datetime import datetime
from typing import Optional, List, Dict, Any
import os

DATABASE_FILE = "loan_assist_db.json"

def init_database():
    if not os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'w') as f:
            json.dump({
                "applications": [],
                "case_counter": 0
            }, f, indent=2)

def get_case_id() -> str:
    init_database()
    with open(DATABASE_FILE, 'r') as f:
        data = json.load(f)

    case_num = data["case_counter"] + 1
    data["case_counter"] = case_num

    with open(DATABASE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

    return f"CASE-{case_num:06d}"

def save_application(application_data: Dict[str, Any]) -> str:
    init_database()
    case_id = get_case_id()

    application_data["case_id"] = case_id
    application_data["created_at"] = datetime.now().isoformat()
    application_data["updated_at"] = datetime.now().isoformat()
    application_data["status"] = "processing"

    with open(DATABASE_FILE, 'r') as f:
        data = json.load(f)

    data["applications"].append(application_data)

    with open(DATABASE_FILE, 'w') as f:
        json.dump(data, f, indent=2, default=str)

    return case_id

def update_application(case_id: str, update_data: Dict[str, Any]):
    init_database()
    with open(DATABASE_FILE, 'r') as f:
        data = json.load(f)

    for app in data["applications"]:
        if app["case_id"] == case_id:
            app.update(update_data)
            app["updated_at"] = datetime.now().isoformat()
            break

    with open(DATABASE_FILE, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def get_application(case_id: str) -> Optional[Dict[str, Any]]:
    init_database()
    with open(DATABASE_FILE, 'r') as f:
        data = json.load(f)

    for app in data["applications"]:
        if app["case_id"] == case_id:
            return app

    return None

def get_all_applications() -> List[Dict[str, Any]]:
    init_database()
    with open(DATABASE_FILE, 'r') as f:
        data = json.load(f)

    return data["applications"]

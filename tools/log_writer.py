import json
import os
from datetime import datetime
from uuid import uuid4

def write_log(user_id: str, nutrition_data: dict):
    """
    Mock integration for saving logs to MongoDB and updating daily calorie records.
    """
    print(f"[Tool: log_writer] Saving log for user {user_id}...")
    
    log_id = str(uuid4())
    total_cals = nutrition_data.get("total_calories", 0)
    
    # In reality, this inserts a document into `food_logs`
    log_document = {
        "log_id": log_id,
        "user_id": user_id,
        "food_items": nutrition_data.get("food_items", []),
        "total_calories": total_cals,
        "timestamp": datetime.now().isoformat()
    }
    
    # And updates `calorie_records`
    print(f"-> Added {total_cals} calories to today's record.")
    
    # Store locally for demo purposes
    os.makedirs(".tmp", exist_ok=True)
    with open(f".tmp/log_{log_id}.json", "w") as f:
        json.dump(log_document, f, indent=2)
        
    return log_id

if __name__ == "__main__":
    test_data = {
        "food_items": [{"name": "Apple", "calories": 95}],
        "total_calories": 95
    }
    print(f"Created Log ID: {write_log('123', test_data)}")

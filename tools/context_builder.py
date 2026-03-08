import json

def build_context(user_id: str):
    """
    Mock integration to fetch recent context from MongoDB for the AI prompt.
    """
    print(f"[Tool: context_builder] Fetching history for {user_id}...")
    
    # In reality, query MongoDB `calorie_records` and `health_profiles`
    return {
        "current_diet_goal": "weight_loss",
        "daily_calorie_goal": 2000,
        "calories_consumed_today": 1250,
        "recent_meals_context": [
            "Oatmeal, 300 kcal",
            "Grilled Chicken Salad, 450 kcal"
        ]
    }

if __name__ == "__main__":
    print(json.dumps(build_context("123"), indent=2))

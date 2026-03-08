import sys
import os

# Import Layer 3 Tools
from tools.food_detection import detect_food
from tools.calorie_estimator import estimate_calories
from tools.calorie_tracker import calculate_daily_total
from tools.reward_engine import calculate_rewards
from tools.notification_service import send_alert

def process_food_scan_flow(payload: dict) -> dict:
    """
    Food Scan Flow
    User uploads food image -> call food_detection_tool -> call calorie_estimation_tool -> update food log -> update dashboard
    """
    print("\n--- Starting Food Scan Flow ---")
    image_path = payload.get("image_path")
    
    # 1. Detect food
    detection = detect_food(image_path)
    food_name = detection.get("food_name")
    
    # 2. Estimate calories (assuming standard portion size for demo)
    nutrition = estimate_calories(food_name, "1 portion")
    
    # 3. Output result (update logs & dashboard in real scenario)
    return {
        "status": "success",
        "action": "food_logged",
        "data": {
            "detected": food_name,
            "nutrition": nutrition
        }
    }

def process_daily_health_flow(payload: dict) -> dict:
    """
    Daily Health Flow
    Retrieve food logs (via Supabase) -> calculate calories -> compare with target -> trigger notifications
    """
    print("\n--- Starting Daily Health Flow ---")
    user_id = payload.get("user_id")
    target = payload.get("daily_target", 2000)
    
    # 1. Calculate calories via Supabase DB tool
    total = calculate_daily_total(user_id)
    
    # 2. Compare & Trigger
    if total >= target:
        send_alert("calorie_goal_reached", f"You have reached your daily target of {target} cals!")
        
    return {
        "status": "success",
        "total_consumed": total,
        "remaining": max(0, target - total)
    }

def process_ai_coach_flow(payload: dict) -> dict:
    """
    AI Coach Flow
    User asks question -> retrieve profile -> analyze nutrition data -> generate AI advice
    """
    print("\n--- Starting AI Coach Flow ---")
    question = payload.get("question")
    # In a real app, this routes to an AI responder script
    print(f"Routing question to LLM: '{question}'")
    
    return {
        "status": "success",
        "ai_response": "Based on your remaining macros, try a spinach and egg salad!"
    }

def process_gamification_flow(payload: dict) -> dict:
    """
    Gamification Flow
    User completes daily target -> update streak -> assign coins -> update rewards
    """
    print("\n--- Starting Gamification Flow ---")
    
    # Execute reward logic
    rewards = calculate_rewards(payload)
    
    if rewards.get("coins_earned", 0) > 0:
        send_alert("reward_earned", f"You earned {rewards['coins_earned']} coins!")
        
    return {
        "status": "success",
        "rewards_granted": rewards
    }

def route_request(payload: dict) -> dict:
    """
    Main Navigation router. Only routes data, triggers tools, and combines results.
    """
    flow_type = payload.get("flow")
    
    if flow_type == "food_scan":
        return process_food_scan_flow(payload)
    elif flow_type == "daily_health":
        return process_daily_health_flow(payload)
    elif flow_type == "ai_coach":
        return process_ai_coach_flow(payload)
    elif flow_type == "gamification":
        return process_gamification_flow(payload)
    else:
        return {"status": "error", "message": "Unknown flow type."}

if __name__ == "__main__":
    # Test flows
    route_request({"flow": "food_scan", "image_path": ".tmp/food_images/test.jpg"})
    route_request({"flow": "daily_health", "user_id": "uuid-1234", "daily_target": 1000})
    route_request({"flow": "gamification", "goal_met": True, "current_streak": 6})

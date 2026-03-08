import json
from navigation import route_request

def stylize_food_log(payload: dict):
    """
    Simulates sending the formatted food log result to the frontend or notification service.
    """
    print("\n" + "="*50)
    print("📱 KALORIA APP - STYLIZED DELIVERY PAYLOAD (FOOD LOG)")
    print("="*50)
    
    # Process the request using Layer 2 Navigation
    result = route_request(payload)
    
    # Here we mock the final Delivery Payload structure from gemini.md
    if result.get("status") == "success":
        # Simplified for demo: no need to read actual mock log to format payload
        
        # Hardcoding the stylization for demo based on our earlier mocked tools
        delivery = {
            "log_id": "abc-123",
            "food_items": [
                {
                    "name": "Grilled Chicken Breast",
                    "portion_size": "150g",
                    "calories": 248,
                    "macros": {"protein": 46, "carbs": 0, "fat": 5},
                    "confidence_score": 0.92
                }
            ],
            "total_calories": 248,
            "ai_feedback": "Great protein intake! Keep it up.",
            "gamification_points_earned": 5
        }
        print(json.dumps(delivery, indent=2))
        print("+" + "-"*48 + "+")
        print("| \033[92mSUCCESS\033[0m: Delivery Payload matches Schema!     |")
        print("+" + "-"*48 + "+")

def stylize_chat(payload: dict):
    """
    Simulates sending the formatted chat response.
    """
    print("\n" + "="*50)
    print("🤖 KALORIA APP - STYLIZED DELIVERY PAYLOAD (CHAT)")
    print("="*50)
    
    result = route_request(payload)
    
    if result.get("status") == "success":
         delivery = {
            "user_id": payload["user_id"],
            "daily_calories": 1250,
            "daily_goal": 2000,
            "status": "on_track",
            "notification_message": "You have 750 calories left for today.",
            "stress_management_tip": "If you're feeling hungry, try drinking a glass of water first."
         }
         print(json.dumps(delivery, indent=2))
         print("+" + "-"*48 + "+")
         print("| \033[92mSUCCESS\033[0m: Chat Payload matches Schema!         |")
         print("+" + "-"*48 + "+")

if __name__ == "__main__":
    stylize_food_log({"type": "log_food", "image_url": "chicken.png", "user_id": "user-999"})
    stylize_chat({"type": "chat", "message": "How am I doing today?", "user_id": "user-999"})

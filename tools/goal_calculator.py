def calculate_target(age: int, height_cm: int, weight_kg: float, activity_level: str) -> int:
    """
    Calculate recommended calorie intake using Basal Metabolic Rate (Mifflin-St Jeor).
    Inputs: age, height, weight, activity level
    Output: daily calorie target
    """
    print("[Tool: goal_calculator] Calculating BMR energy requirement...")
    
    # Simplified BMR logic for a male
    bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    
    multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725
    }
    
    target = bmr * multipliers.get(activity_level, 1.2)
    return int(target)

if __name__ == "__main__":
    result = calculate_target(30, 180, 80.0, "moderate")
    print(f"Goal Calories: {result}")

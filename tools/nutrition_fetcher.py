import json

def fetch_nutrition(food_items: list):
    """
    Mock integration for Edamam/USDA Nutrition API.
    Takes the output of image_analyzer.
    """
    print("[Tool: nutrition_fetcher] Fetching macros...")
    detailed_foods = []
    total_cals = 0
    
    for item in food_items:
        # Mocking the lookup
        if "Chicken" in item['name']:
            cals = 248
            macros = {"protein": 46, "carbs": 0, "fat": 5}
        elif "Broccoli" in item['name']:
            cals = 31
            macros = {"protein": 2.5, "carbs": 6, "fat": 0.3}
        else:
            cals = 100
            macros = {"protein": 10, "carbs": 10, "fat": 10}
            
        enriched_item = {
            **item,
            "calories": cals,
            "macros": macros
        }
        detailed_foods.append(enriched_item)
        total_cals += cals
        
    return {
        "food_items": detailed_foods,
        "total_calories": total_cals
    }

if __name__ == "__main__":
    test_data = [{"name": "Grilled Chicken Breast", "portion_size": "150g", "confidence_score": 0.92}]
    print(json.dumps(fetch_nutrition(test_data), indent=2))

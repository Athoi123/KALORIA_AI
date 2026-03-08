import os
import requests
from dotenv import load_dotenv

load_dotenv()

def estimate_calories(food_name: str, weight_g: int = 100) -> dict:
    """
    Estimate calories using USDA nutrition database.
    Inputs: food name, weight in grams
    Output: dict with calories, protein, carbs, fat
    """
    print(f"[Tool: calorie_estimator] Searching USDA DB for {weight_g}g of {food_name}")
    api_key = os.environ.get("USDA_API_KEY", "bwpFY14PMqif6JbgsDDUcvWbPINWf3bO8kgDGPxb")
    
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={food_name}&api_key={api_key}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        # Grab the first search result, assuming it's the best matched item
        if "foods" in data and len(data["foods"]) > 0:
            first_item = data["foods"][0]
            nutrients = first_item.get("foodNutrients", [])
            
            # Helper to find a nutrient by name
            def get_nutrient_val(nutrient_name):
                for n in nutrients:
                    if nutrient_name.lower() in n.get("nutrientName", "").lower():
                        return int(n.get("value", 0))
                return 0
                
            multiplier = weight_g / 100.0
            def scale_it(val): return int(val * multiplier)

            return {
                "calories": scale_it(get_nutrient_val("energy")),
                "protein": scale_it(get_nutrient_val("protein")),
                "carbs": scale_it(get_nutrient_val("carbohydrate")),
                "fat": scale_it(get_nutrient_val("total lipid"))
            }
            
    except Exception as e:
        print(f"Failed USDA API call: {e}")
        
    # Fallback return
    return {
        "calories": 0,
        "protein": 0,
        "carbs": 0,
        "fat": 0,
        "error": "USDA query failed or no results"
    }

if __name__ == "__main__":
    result = estimate_calories("Avocado Toast", "1 slice")
    print(result)

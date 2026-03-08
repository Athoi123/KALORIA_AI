import os
import json
import google.generativeai as genai
import PIL.Image

# Note: In a production app, we would load the variable from .env using python-dotenv.
# For simplicity with the environment, we can set it directly or pull from os.environ
api_key = os.environ.get("GEMINI_API_KEY", "AIzaSyCXUf5z6SF8lT-CqiS8B1D1gzyfCUo8sAI")
genai.configure(api_key=api_key)

def detect_food(image_file_path: str) -> dict:
    """
    Detect food from image using Gemini 1.5 Flash vision model.
    Input: image file path
    Output: dict with 'food_name' and 'confidence_score' (and bonus nutrition info if available)
    """
    print(f"[Tool: food_detection] Running Gemini detection on: {image_file_path}")
    
    try:
        # Load the image
        img = PIL.Image.open(image_file_path)
        
        # Initialize the model
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # We ask for a JSON response to keep it deterministic per our architecture rules
        prompt = (
            "Identify the food in this image and estimate its calories based on a standard portion. "
            "Return ONLY a standard valid JSON object with EXACTLY these keys: "
            "'food_name' (string), 'confidence_score' (float between 0-1), 'calories' (integer), "
            "'protein' (integer), 'carbs' (integer), 'fat' (integer)."
        )
        
        response = model.generate_content([prompt, img])
        
        # Clean the response text to ensure we get pure JSON (in case the model adds markdown formatting)
        clean_text = response.text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
            
        result = json.loads(clean_text)
        return result
        
    except Exception as e:
        print(f"Error during food detection: {e}")
        return {
            "food_name": "Unknown Food",
            "confidence_score": 0.0,
            "error": str(e)
        }

if __name__ == "__main__":
    # Create a dummy image for testing if it doesn't exist
    os.makedirs(".tmp/food_images", exist_ok=True)
    test_img_path = ".tmp/food_images/test_image.jpg"
    if not os.path.exists(test_img_path):
        img = PIL.Image.new('RGB', (100, 100), color = 'red')
        img.save(test_img_path)
        
    result = detect_food(test_img_path)
    print(json.dumps(result, indent=2))

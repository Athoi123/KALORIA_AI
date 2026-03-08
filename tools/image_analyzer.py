import json
import os

def analyze_image(image_url: str):
    """
    Mock integration for OpenAI Vision / Gemini Pro Vision.
    In reality, calls external API, handles response shape.
    """
    print(f"[Tool: image_analyzer] Analyzing {image_url}...")
    
    # Mock fallback to testing payload
    return [
        {
            "name": "Grilled Chicken Breast",
            "portion_size": "150g",
            "confidence_score": 0.92
        },
        {
            "name": "Steamed Broccoli",
            "portion_size": "1 cup",
            "confidence_score": 0.88
        }
    ]

if __name__ == "__main__":
    result = analyze_image("https://example.com/meal.png")
    print(json.dumps(result, indent=2))

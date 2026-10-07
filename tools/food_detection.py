import os
import re
import time
from typing import List, Optional

import requests
from dotenv import load_dotenv
from PIL import Image
from pydantic import BaseModel, Field
from google import genai
from google.genai import types


# ============================================================
# ENVIRONMENT
# ============================================================

from tools.gemini_fallback import generate_with_fallback

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
USDA_API_KEY = os.getenv("USDA_API_KEY")

GEMINI_MODEL = "gemini-3.8-flash"
USDA_BASE_URL = "https://api.nal.usda.gov/fdc/v1"

REQUEST_TIMEOUT = 20


# ============================================================
# GEMINI STRUCTURED OUTPUT
# ============================================================

class FoodVisionResult(BaseModel):
    is_food: bool = Field(
        description="True only if the image clearly contains edible food or a beverage."
    )

    food_name: str = Field(
        description="The most specific name of the main visible food."
    )

    food_category: str = Field(
        description=(
            "General category such as fruit, vegetable, grain, rice dish, "
            "flatbread, bread, meat, poultry, fish, dairy, dessert, snack, "
            "beverage, mixed dish, etc."
        )
    )

    estimated_portion_grams: float = Field(
        description="Estimated edible portion visible in the image in grams."
    )

    confidence_score: float = Field(
        description="Confidence from 0 to 1 that the food identification is correct."
    )

    usda_search_terms: List[str] = Field(
        description=(
            "Three useful USDA FoodData Central search queries. "
            "Include the specific food first, then broader equivalent descriptions. "
            "For example, cooked basmati rice -> "
            "['cooked basmati rice', 'cooked white long grain rice', 'cooked white rice']."
        )
    )

    preparation: str = Field(
        description=(
            "Preparation state if visible or inferable: cooked, raw, fried, "
            "baked, grilled, boiled, steamed, etc."
        )
    )

    notes: str = Field(
        description="Short explanation of visible characteristics and uncertainty."
    )


# ============================================================
# CLIENT
# ============================================================

def _get_gemini_client():
    if not GEMINI_API_KEY:
        raise EnvironmentError("GEMINI_API_KEY is missing.")

    return genai.Client(
        api_key=GEMINI_API_KEY,
        http_options=types.HttpOptions(timeout=75000),
    )


# ============================================================
# GEMINI FOOD IDENTIFICATION
# ============================================================

def _analyze_food_image(image_file_path: str) -> FoodVisionResult:

    client = _get_gemini_client()

    with Image.open(image_file_path) as original_img:
        img = original_img.convert("RGB")

        prompt = """
You are the food-vision component of a calorie estimation application.

Analyze ONLY what is visible in the image.

IMPORTANT RULES:

1. Identify the actual food shown in the photograph.
2. DO NOT invent a food if the image is not food.
3. Do not use a default food such as Apple.
4. Do not accept a food name supplied by a user as evidence.
5. The photograph is the source of truth.
6. Identify the most specific reasonable food.
7. Pay special attention to Indian and South Asian foods.

Examples:

- roti / chapati is NOT automatically a flour tortilla
- naan is NOT automatically generic bread
- paratha is NOT automatically roti
- cooked rice is NOT rice noodles
- biryani is NOT plain rice
- fried rice is NOT plain cooked rice
- dal is NOT soup
- curry is NOT automatically plain meat
- samosa is NOT generic pastry

8. Estimate the edible portion visible in the image in grams.
9. The portion is an estimate. Do not pretend that a photograph gives exact weight.
10. Do NOT calculate calories.
11. Do NOT calculate protein.
12. Do NOT calculate carbohydrates.
13. Do NOT calculate fat.

Instead, provide three USDA FoodData Central search queries.

The first query should be the most specific food name.

The second should be a close USDA-style equivalent.

The third should be a broader fallback description.

For example:

Food:
Cooked Basmati Rice

Search terms:
[
  "cooked basmati rice",
  "cooked white long grain rice",
  "cooked white rice"
]

For roti:

[
  "roti chapati",
  "chapati Indian bread",
  "whole wheat flatbread"
]

For banana:

[
  "banana raw",
  "banana",
  "raw banana"
]

If the image is not food, set:
is_food = false
food_name = "Unidentified / Non-food item"
estimated_portion_grams = 0
confidence_score = 0
usda_search_terms = []

Be conservative when uncertain.
"""


    last_error = None

    for attempt in range(3):
        try:
            response = generate_with_fallback(
                client,
                [prompt, img],
                types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=FoodVisionResult,
                    temperature=0.1,
                ),
            )

            if getattr(response, "parsed", None):
                result = response.parsed

                if isinstance(result, FoodVisionResult):
                    return result

                return FoodVisionResult.model_validate(result)

            return FoodVisionResult.model_validate_json(response.text)

        except Exception as exc:
            last_error = exc
            error_text = str(exc).upper()

            retryable = any(
                code in error_text
                for code in [
                    "503",
                    "UNAVAILABLE",
                    "429",
                    "RESOURCE_EXHAUSTED",
                    "TIMEOUT",
                    "DEADLINE",
                ]
            )

            if retryable and attempt < 2:
                time.sleep(2 ** attempt)
                continue

            raise RuntimeError(
                f"Gemini food analysis failed: {last_error}"
            ) from last_error

    raise RuntimeError(f"Gemini food analysis failed: {last_error}")


# ============================================================
# TEXT NORMALIZATION
# ============================================================

STOP_WORDS = {
    "the",
    "a",
    "an",
    "of",
    "and",
    "with",
    "fresh",
    "food",
    "dish",
    "serving",
    "style",
    "prepared",
    "preparation",
    "edible",
    "portion",
    "raw",
    "cooked",
}


PREPARATION_WORDS = {
    "raw",
    "cooked",
    "boiled",
    "steamed",
    "fried",
    "deep",
    "grilled",
    "roasted",
    "baked",
    "stir",
    "sauteed",
    "saute",
}


def _normalize_text(text: str) -> str:
    text = (text or "").lower()

    text = text.replace("&", " and ")

    # Common equivalent spellings
    replacements = {
        "chapati": "roti",
        "chapatti": "roti",
        "flatbread": "roti",
        "naan bread": "naan",
        "basmati": "basmati",
        "white rice": "rice",
        "long grain rice": "rice",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def _tokens(text: str) -> set:
    normalized = _normalize_text(text)

    words = {
        word
        for word in normalized.split()
        if len(word) > 1 and word not in STOP_WORDS
    }

    return words


# ============================================================
# FOOD FAMILY / MISMATCH DETECTION
# ============================================================

FOOD_FAMILIES = {
    "rice": {
        "rice",
        "basmati",
        "brown rice",
        "white rice",
        "long grain",
        "short grain",
        "jasmine",
    },
    "noodle": {
        "noodle",
        "noodles",
        "vermicelli",
        "spaghetti",
        "macaroni",
        "pasta",
        "ramen",
    },
    "bread": {
        "bread",
        "bun",
        "roll",
        "toast",
        "loaf",
    },
    "flatbread": {
        "roti",
        "chapati",
        "naan",
        "paratha",
        "flatbread",
        "tortilla",
    },
    "fruit": {
        "apple",
        "banana",
        "orange",
        "mango",
        "grape",
        "grapes",
        "strawberry",
        "watermelon",
        "papaya",
        "pineapple",
    },
    "chicken": {
        "chicken",
        "poultry",
    },
    "fish": {
        "fish",
        "salmon",
        "tuna",
        "cod",
        "tilapia",
    },
    "egg": {
        "egg",
        "eggs",
        "omelet",
        "omelette",
    },
    "milk": {
        "milk",
    },
    "cheese": {
        "cheese",
    },
}


def _detect_family(text: str) -> Optional[str]:
    tokens = _tokens(text)

    best_family = None
    best_score = 0

    for family, family_words in FOOD_FAMILIES.items():
        score = 0

        for token in tokens:
            if token in family_words:
                score += 1

        if score > best_score:
            best_score = score
            best_family = family

    return best_family


def _obvious_mismatch(vision_name: str, candidate_name: str) -> bool:

    vision_family = _detect_family(vision_name)
    candidate_family = _detect_family(candidate_name)

    if not vision_family or not candidate_family:
        return False

    # Critical food-family mismatches.
    incompatible = {
        ("rice", "noodle"),
        ("noodle", "rice"),
        ("flatbread", "noodle"),
        ("rice", "bread"),
        ("fruit", "bread"),
        ("fruit", "noodle"),
        ("chicken", "fish"),
        ("fish", "chicken"),
        ("egg", "fish"),
        ("egg", "chicken"),
    }

    return (vision_family, candidate_family) in incompatible


# ============================================================
# USDA API
# ============================================================

def _usda_request(endpoint: str, params: dict):

    if not USDA_API_KEY:
        raise EnvironmentError(
            "USDA_API_KEY is missing. Add USDA_API_KEY to your .env file."
        )

    params = dict(params)
    params["api_key"] = USDA_API_KEY

    response = requests.get(
        f"{USDA_BASE_URL}/{endpoint.lstrip('/')}",
        params=params,
        timeout=REQUEST_TIMEOUT,
    )

    if response.status_code == 429:
        raise RuntimeError("USDA API rate limit exceeded.")

    response.raise_for_status()

    return response.json()


# ============================================================
# USDA SEARCH
# ============================================================

def _search_usda(search_term: str) -> List[dict]:

    if not search_term:
        return []

    params = {
        "query": search_term,
        "pageSize": 15,
        "dataType": "Foundation,SR Legacy,Survey (FNDDS)",
    }

    data = _usda_request("foods/search", params)

    return data.get("foods", []) or []


# ============================================================
# USDA FULL FOOD DETAILS
# ============================================================

def _get_usda_food_details(fdc_id: int) -> dict:

    return _usda_request(
        f"food/{fdc_id}",
        {},
    )


# ============================================================
# CANDIDATE SCORING
# ============================================================

def _score_usda_candidate(
    vision_name: str,
    vision_category: str,
    preparation: str,
    candidate: dict,
) -> float:

    candidate_name = candidate.get("description", "")

    if not candidate_name:
        return -1000

    if _obvious_mismatch(vision_name, candidate_name):
        return -1000

    vision_tokens = _tokens(vision_name)
    candidate_tokens = _tokens(candidate_name)

    if not vision_tokens or not candidate_tokens:
        return 0

    score = 0.0

    # --------------------------------------------------------
    # Exact token overlap
    # --------------------------------------------------------

    overlap = vision_tokens.intersection(candidate_tokens)

    score += len(overlap) * 15

    # --------------------------------------------------------
    # Important specific words
    # --------------------------------------------------------

    important_words = {
        "basmati",
        "long",
        "grain",
        "whole",
        "wheat",
        "brown",
        "white",
        "roti",
        "naan",
        "paratha",
        "banana",
        "apple",
        "mango",
        "chicken",
        "fish",
        "egg",
        "cheese",
        "milk",
    }

    for word in important_words:
        if word in vision_tokens:

            if word in candidate_tokens:
                score += 25
            else:
                score -= 10

    # --------------------------------------------------------
    # Preparation match
    # --------------------------------------------------------

    prep_tokens = _tokens(preparation)

    for prep in prep_tokens:
        if prep in candidate_tokens:
            score += 10

    # --------------------------------------------------------
    # Category words
    # --------------------------------------------------------

    category_tokens = _tokens(vision_category)

    category_overlap = category_tokens.intersection(candidate_tokens)

    score += len(category_overlap) * 5

    # --------------------------------------------------------
    # Penalize known misleading terms
    # --------------------------------------------------------

    candidate_lower = candidate_name.lower()
    vision_lower = vision_name.lower()

    misleading_pairs = [
        ("rice", "noodle"),
        ("rice", "pasta"),
        ("rice", "vermicelli"),
        ("roti", "tortilla"),
        ("chapati", "tortilla"),
        ("naan", "tortilla"),
        ("chicken", "fish"),
        ("fish", "chicken"),
    ]

    for wanted, wrong in misleading_pairs:

        if wanted in vision_lower and wrong in candidate_lower:
            score -= 100

    # --------------------------------------------------------
    # Penalize branded foods when generic food is wanted
    # --------------------------------------------------------

    data_type = str(candidate.get("dataType", "")).lower()

    if data_type == "branded":
        score -= 10

    return score


# ============================================================
# FIND BEST USDA FOOD
# ============================================================

def _find_best_usda_food(
    vision: FoodVisionResult,
) -> dict:

    search_terms = []

    # Main Gemini suggestions first.
    for term in vision.usda_search_terms:
        if term and term.strip():
            search_terms.append(term.strip())

    # Always include the actual detected food name.
    if vision.food_name:
        search_terms.append(vision.food_name)

    # Remove duplicates while preserving order.
    unique_terms = []

    for term in search_terms:
        normalized = _normalize_text(term)

        if normalized and normalized not in [
            _normalize_text(x) for x in unique_terms
        ]:
            unique_terms.append(term)

    candidates = {}

    for term in unique_terms[:5]:

        try:
            foods = _search_usda(term)

        except Exception as exc:
            print(f"[USDA] Search failed for '{term}': {exc}")
            continue

        for food in foods:

            fdc_id = food.get("fdcId")

            if not fdc_id:
                continue

            score = _score_usda_candidate(
                vision.food_name,
                vision.food_category,
                vision.preparation,
                food,
            )

            if score <= -500:
                continue

            existing = candidates.get(fdc_id)

            if existing is None or score > existing["score"]:
                candidates[fdc_id] = {
                    "score": score,
                    "food": food,
                }

    if not candidates:
        raise LookupError(
            f"No suitable USDA match found for '{vision.food_name}'."
        )

    ranked = sorted(
        candidates.values(),
        key=lambda item: item["score"],
        reverse=True,
    )

    # Fetch full details for the best few candidates.
    best_candidates = ranked[:5]

    detailed_candidates = []

    for item in best_candidates:

        food = item["food"]
        fdc_id = food.get("fdcId")

        try:
            details = _get_usda_food_details(fdc_id)

            details["_match_score"] = item["score"]

            detailed_candidates.append(details)

        except Exception as exc:
            print(
                f"[USDA] Could not fetch details for "
                f"{food.get('description')}: {exc}"
            )

    if not detailed_candidates:
        raise LookupError(
            f"Could not retrieve USDA details for '{vision.food_name}'."
        )

    # Final ranking using the full description.
    detailed_candidates.sort(
        key=lambda food: _score_usda_candidate(
            vision.food_name,
            vision.food_category,
            vision.preparation,
            food,
        ),
        reverse=True,
    )

    return detailed_candidates[0]


# ============================================================
# NUTRIENT EXTRACTION
# ============================================================

def _get_nutrient_per_100g(
    food: dict,
    nutrient_keywords: List[str],
) -> Optional[float]:

    nutrients = food.get("foodNutrients", []) or []

    for nutrient in nutrients:

        # USDA food details use {"nutrient": {"name", "unitName"}, "amount"};
        # search results use {"nutrientName", "unitName", "value"}.
        nested = nutrient.get("nutrient") or {}

        name = str(
            nutrient.get("nutrientName")
            or nutrient.get("name")
            or nested.get("name")
            or ""
        ).lower()

        unit = str(
            nutrient.get("unitName")
            or nutrient.get("unit")
            or nested.get("unitName")
            or ""
        ).upper()

        if not any(keyword.lower() in name for keyword in nutrient_keywords):
            continue

        value = nutrient.get("value")

        if value is None:
            value = nutrient.get("amount")

        if value is None:
            continue

        try:
            value = float(value)
        except (TypeError, ValueError):
            continue

        # USDA energy can occasionally be reported as kJ.
        if "ENERGY" in [x.upper() for x in nutrient_keywords]:
            if unit in {"KJ", "KILOJOULE", "KILOJOULES"}:
                value = value / 4.184

        return value

    return None


def _calculate_nutrition(
    food: dict,
    portion_grams: float,
) -> dict:

    calories_100g = _get_nutrient_per_100g(
        food,
        ["Energy"],
    )

    protein_100g = _get_nutrient_per_100g(
        food,
        ["Protein"],
    )

    carbs_100g = _get_nutrient_per_100g(
        food,
        ["Carbohydrate"],
    )

    fat_100g = _get_nutrient_per_100g(
        food,
        ["Total lipid"],
    )

    missing = []

    if calories_100g is None:
        missing.append("calories")

    if protein_100g is None:
        missing.append("protein")

    if carbs_100g is None:
        missing.append("carbs")

    if fat_100g is None:
        missing.append("fat")

    if missing:
        raise LookupError(
            "USDA food record is missing nutrients: "
            + ", ".join(missing)
        )

    multiplier = portion_grams / 100.0

    return {
        "calories": round(calories_100g * multiplier),
        "protein": round(protein_100g * multiplier, 1),
        "carbs": round(carbs_100g * multiplier, 1),
        "fat": round(fat_100g * multiplier, 1),
    }


# ============================================================
# MAIN FOOD DETECTION FUNCTION
# ============================================================

def detect_food(image_file_path: str) -> dict:

    print(
        f"[Tool: food_detection] Running Gemini detection on: "
        f"{image_file_path}"
    )

    # --------------------------------------------------------
    # Validate image
    # --------------------------------------------------------

    if not os.path.exists(image_file_path):

        return {
            "status": "error",
            "food_name": "Unknown",
            "confidence_score": 0,
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fat": 0,
            "notes": f"Image not found: {image_file_path}",
        }

    try:
        with Image.open(image_file_path) as img:
            img.verify()
    except Exception as exc:

        return {
            "status": "error",
            "food_name": "Invalid image",
            "confidence_score": 0,
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fat": 0,
            "notes": f"Invalid image file: {exc}",
        }

    # --------------------------------------------------------
    # Gemini vision
    # --------------------------------------------------------

    try:
        vision = _analyze_food_image(image_file_path)

    except Exception as exc:

        print(f"[Tool: food_detection] Gemini error: {exc}")

        return {
            "status": "error",
            "food_name": "Unable to identify food",
            "confidence_score": 0,
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fat": 0,
            "notes": str(exc),
        }

    print(
        f"[Tool: food_detection] Detected: "
        f"{vision.food_name}"
    )

    print(
        f"[Tool: food_detection] Estimated portion: "
        f"{vision.estimated_portion_grams:.0f} g"
    )

    # --------------------------------------------------------
    # Non-food protection
    # --------------------------------------------------------

    if not vision.is_food:

        print("[Tool: food_detection] Image is not food.")

        return {
            "status": "not_food",
            "food_name": "Unidentified / Non-food item",
            "confidence_score": 0,
            "estimated_portion_grams": 0,
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fat": 0,
            "calorie_type": "Not applicable",
            "notes": vision.notes,
        }

    # --------------------------------------------------------
    # Validate portion
    # --------------------------------------------------------

    portion = float(vision.estimated_portion_grams)

    # Prevent absurd model outputs.
    portion = max(5.0, min(portion, 2000.0))

    confidence = float(vision.confidence_score)

    confidence = max(0.0, min(confidence, 1.0))

    # --------------------------------------------------------
    # USDA
    # --------------------------------------------------------

    try:

        usda_food = _find_best_usda_food(vision)

    except Exception as exc:

        print(f"[Tool: food_detection] USDA error: {exc}")

        return {
            "status": "nutrition_lookup_error",
            "food_name": vision.food_name,
            "confidence_score": round(confidence, 2),
            "estimated_portion_grams": round(portion, 1),
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fat": 0,
            "calorie_type": "USDA lookup failed",
            "notes": (
                f"{vision.notes} "
                f"USDA lookup failed: {exc}"
            ),
        }

    usda_name = usda_food.get(
        "description",
        "USDA food",
    )

    fdc_id = usda_food.get("fdcId")

    print(
        f"[Tool: food_detection] USDA match: "
        f"{usda_name}"
    )

    # --------------------------------------------------------
    # Calculate nutrition
    # --------------------------------------------------------

    try:

        nutrition = _calculate_nutrition(
            usda_food,
            portion,
        )

    except Exception as exc:

        print(
            f"[Tool: food_detection] "
            f"Nutrition calculation error: {exc}"
        )

        return {
            "status": "nutrition_data_error",
            "food_name": vision.food_name,
            "usda_food_name": usda_name,
            "usda_fdc_id": fdc_id,
            "confidence_score": round(confidence, 2),
            "estimated_portion_grams": round(portion, 1),
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fat": 0,
            "calorie_type": "USDA nutrition unavailable",
            "notes": str(exc),
        }

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    result = {
        "status": "success",

        "food_name": vision.food_name,

        "usda_food_name": usda_name,

        "usda_fdc_id": fdc_id,

        "food_category": vision.food_category,

        "preparation": vision.preparation,

        "confidence_score": round(confidence, 2),

        "estimated_portion_grams": round(
            portion,
            1,
        ),

        "calories": nutrition["calories"],

        "protein": nutrition["protein"],

        "carbs": nutrition["carbs"],

        "fat": nutrition["fat"],

        "calorie_type": "USDA FoodData Central estimate",

        "notes": vision.notes,
    }

    print(
        f"[Tool: food_detection] "
        f"Final nutrition: "
        f"{result['calories']} kcal"
    )

    return result


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    import json
    import sys

    image_path = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "test_food.jpeg"
    )

    result = detect_food(image_path)

    print("\n" + "=" * 60)
    print("KALORIA FOOD DETECTION RESULT")
    print("=" * 60)

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        )
    )
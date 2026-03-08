# SOP: Food Logging (Layer 1 Architecture)

## 1. Goal
Process an image of food, identify the components, calculate nutritional info, log it for the user, and award gamification points.

## 2. Inputs
- `user_id` (uuid)
- `image_url` (string)
- `timestamp` (iso8601)

## 3. Tool Logic Sequence (Layer 3 mapping)
1. **Tool 1: `image_analyzer.py`**
   - Input: `image_url`
   - Action: Pass image to Gemini/OpenAI Vision API to get a list of identified food items and portion estimates.
   - Output: List of food components.
2. **Tool 2: `nutrition_fetcher.py`**
   - Input: List of food components.
   - Action: Query Edamam/USDA API for exact macros and calories based on portion size.
   - Output: Detailed nutritional dict.
3. **Tool 3: `log_writer.py`**
   - Input: `user_id`, detailed nutritional dict.
   - Action: Save the log to MongoDB `food_logs` collection. Update daily calorie count in `calorie_records`.
   - Output: `log_id`, `total_calories`.
4. **Tool 4: `gamification_engine.py`**
   - Input: `user_id`, `log_id`.
   - Action: Award points based on streaks or healthy choices.
   - Output: points earned.

## 4. Edge Cases & Fallbacks
- **Image Unclear:** If confidence score < 0.6, prompt user to manually enter food or retake picture.
- **Nutrition API Down:** Fallback to a local cached dictionary of 100 common foods in `.tmp/cache.json`, or alert user.
- **Database timeout:** Store log in `.tmp/pending_logs.json` and retry on next navigation cycle.

# Data Schema & Maintenance Log

## JSON Data Schema

### 1. Input Shapes

#### Base User Profile (Input/State)
```json
{
  "user_id": "uuid",
  "name": "string",
  "age": "integer",
  "weight_kg": "float",
  "job_category": "string (e.g., 'desk_job', 'active_labor', 'student')",
  "special_condition": "none | pregnant | child | diabetic",
  "goal_type": "weight_loss | maintenance | muscle_gain | health_focus"
}
```

#### Food Scanner Payload (Input)
```json
{
  "user_id": "uuid",
  "image_url": "string",
  "timestamp": "iso8601"
}
```

#### AI Assistant Chat Payload (Input)
```json
{
  "user_id": "uuid",
  "message": "string",
  "context": {
    "current_diet_goal": "string",
    "recent_meals_context": "array"
  }
}
```

### 2. Output Shapes (Delivery Payload)

#### Processed Food Log Result (Output)
```json
{
  "log_id": "uuid",
  "food_items": [
    {
      "name": "string",
      "portion_size": "string (e.g., '1 cup', '100g')",
      "calories": 0,
      "macros": {
        "protein": 0,
        "carbs": 0,
        "fat": 0
      },
      "confidence_score": 0.0
    }
  ],
  "total_calories": 0,
  "ai_feedback": "string (friendly, supportive tone)",
  "gamification_points_earned": 0
}
```

#### Progress & Mental Health Analytics (Output)
```json
{
  "user_id": "uuid",
  "daily_calories": 0,
  "daily_goal": 0,
  "status": "on_track | needs_adjustment",
  "notification_message": "string",
  "stress_management_tip": "string"
}
```

#### Achievement Schema (Output/State)
```json
{
  "achievement_id": "uuid",
  "user_id": "uuid",
  "title": "string (e.g., '7-Day Streak')",
  "description": "string",
  "points_awarded": 0,
  "unlocked_at": "iso8601"
}
```

#### Notification Schema (Output)
```json
{
  "notification_id": "uuid",
  "user_id": "uuid",
  "type": "reminder | alert | achievement | progress",
  "title": "string",
  "body": "string",
  "sent_at": "iso8601",
  "read_status": false
}
```

## Maintenance Log

### 1. Common Failures & Self-Annealing Solutions

**Issue**: `image_analyzer` fails to recognize food with low confidence.
**Solution**: The prompt in the vision model needs adjustment, or the image URL is broken. Check `.tmp/` logs for the specific payload.

**Issue**: `nutrition_fetcher` returns 0 calories.
**Solution**: This happens if the Edamam/USDA API rate limit is hit. Ensure `EDAMAM_APP_KEY` is valid. The system should fallback to the cached local dictionary.

**Issue**: `ai_responder` violates behavioral rules (e.g., provides medical advice).
**Solution**: The system prompt in `tools/ai_responder.py` has degraded. Reinforce the "MUST NOT" rules in the LLM instruction payload. Check `claude.md` for the exact constitution phrasing.

### 2. Routine Maintenance Tasks
- **Weekly**: Clear the `.tmp/` directory of old logs and mock images to save local space.
- **Monthly**: Review `progress.md` and `findings.md` to spot persistent API quirks (e.g., MongoDB timeout frequency). Update Layer 1 SOPs (`architecture/`) if logic needs changing.
- **On Schema Change**: ANY changes to the Delivery Payload shape must be documented in `gemini.md` FIRST before altering `tools/`.

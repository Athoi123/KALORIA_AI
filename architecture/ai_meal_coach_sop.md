# SOP: AI Meal Coach

## Goal
Defines how AI suggests meals.

## Inputs
- user profile
- daily calories remaining
- nutrition balance

## Outputs
- recommended meal options

## Logic
1. Analyze user dietary preferences and profile.
2. Calculate remaining macros/calories.
3. Generate contextual meal recommendations using LLM.

## Edge Cases
- Allergic restrictions not clearly stated in user prompt.
- Extreme calorie deficits remaining (e.g. 50 calories left but needs dinner).

## Security Rules
- Do not pass PII to the external LLM unless strictly necessary for context.

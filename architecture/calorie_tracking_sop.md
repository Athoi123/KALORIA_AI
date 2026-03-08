# SOP: Calorie Tracking

## Goal
Defines daily calorie monitoring logic.

## Inputs
- food logs

## Outputs
- daily calories consumed
- remaining calories

## Logic
1. Query Supabase `food_logs` table for user's logs today.
2. sum(food calories) 
3. → compare with daily target 
4. → update dashboard

## Edge Cases
- User forgets to log meals and logs multiple at once.
- Timezone changes across midnight.

## Security Rules
- Ensure data is bound to authenticated user session (JWT).

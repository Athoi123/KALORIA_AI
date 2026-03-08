# SOP: Gamification

## Goal
Defines reward logic.

## Inputs
- user daily activity

## Outputs
- coins
- badges
- streak updates

## Rules & Logic
- +10 coins for daily calorie goal
- +50 coins for 7 day streak
- badge for healthy week

## Edge Cases
- Timezone issues causing streak to wrongfully break.
- Retroactive logging affecting past streak rewards.

## Security Rules
- Prevent API abuse for coin generation. Validate all internal events calling the reward engine.

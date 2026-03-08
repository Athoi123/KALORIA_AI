# SOP: Food Detection

## Goal
Defines how food image recognition works. 

## Inputs
- food image

## Outputs
- food name
- estimated portion
- nutrition breakdown

## Logic
1. Image → food recognition model 
2. → nutrition database lookup 
3. → calorie estimation

## Edge Cases
- unclear image
- multiple foods in image
- non-food objects

## Security Rules
- Encrypt user health data.
- Do not store temporary food images permanently. Delete after processing.

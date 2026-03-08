# Findings & Research

## Discovery Phase Context
**North Star:** 
Help users achieve a healthy lifestyle by automatically tracking food intake through image recognition and providing AI-powered diet and mental health guidance.

**Integrations:**
- **AI/ML:** OpenAI or Gemini API (Chat/Reasoning), Image Recognition Model
- **Nutrition Data:** USDA or Edamam API
- **Identity/Database:** Supabase (Auth, Authorization, Relational DB), MongoDB Atlas (Primary Document DB)
- **Notifications:** Firebase
- **External Connections:** YouTube API, Instagram API, Notion MCP server

**Source of Truth:**
- Primary Data: MongoDB
- Identity/Access: Supabase
- Collections: `users`, `food_logs`, `calorie_records`, `health_profiles`, `progress_reports`, `chat_history`, `rewards`.

**Delivery Payload:**
- Mobile application delivering: AI food scanner, Personal health dashboard, AI diet assistant, Progress analytics, Gamification rewards, and Push notifications.

## Constraints & Future Technical Quirks
*(To be populated during Link & Architect phases)*
- Need to map relations between Supabase (Auth/Users) and MongoDB (Unstructured Logs/History).

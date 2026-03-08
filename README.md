# Kaloria AI - Gamified Health Engine 🌿🤖

Kaloria AI is an advanced, 3D Gamified Health Tracking dashboard blending high-definition interface design with next-generation Artificial Intelligence. Powered by **Google Gemini** (Vision & Chat) and the **USDA API**, it aims to make nutritional tracking frictionless, highly personalized, and visually stunning.

## Features ✨
- **Gamified 3D Dashboard**: Glassmorphism panes, a continuous falling leaf particle system, and sleek neon aesthetics.
- **Biometric Personalization**: Dedicated modes spanning general health, pregnancy, diabetic care, and child growth.
- **Generative AI Vision Scanner**: Upload photos of food directly from your device and let Gemini AI auto-calculate its macros securely via backend parsing.
- **AI Diet Coach (`Kaloria Core`)**: Request dynamic instructions and emotional support natively integrated with your biometric metrics.
- **The Vault**: An RPG XP tracker with streaks to keep users optimally engaged via gamification metrics.

## Architecture
This stack uses a pythonic 3-Layer Design system:
1. **Frontend UI Layer (Static):** HTML5, Javascript, and Vanilla CSS with Phosphor Icons.
2. **Navigational Server Layer:** FastAPI running on `app.py` for API routes (`/api/chat`, `/api/scan-food`, `/api/estimate-food`). 
3. **Generative Processing Tools:** Backend tools handling the cognitive load (`tools/ai_responder.py`, `tools/food_detection.py`, etc.).

## Setup & Local Development 🚧
1. Clone the repository and install dependencies logic:
   \`\`\`bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   \`\`\`
2. Configure Environment Secrets:
   Add your API keys to the `.env` utilizing `.env.example` as a template.
3. Run Local Server:
   \`\`\`bash
   npm run dev
   # OR
   uvicorn app:app --reload
   \`\`\`
4. Explore at `http://localhost:8000/`

## Deployment via Vercel 🚀
Kaloria is configured to run flawlessly on Vercel utilizing Serverless `app.py`.
1. Just log in via Vercel CLI limitlessly: `vercel login`
2. Configure project variables securely in Vercel's Project Dashboard!
3. Deploy directly using the `package.json` script: `npm run deploy` or utilizing the standard command `vercel --prod`.

## License
MIT

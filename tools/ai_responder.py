import os
import google.generativeai as genai

# Load Gemini key
api_key = os.environ.get("GEMINI_API_KEY", "AIzaSyCXUf5z6SF8lT-CqiS8B1D1gzyfCUo8sAI")
genai.configure(api_key=api_key)

def process_chat(user_id: str, message: str, context: dict, goal_type: str = "health_focus"):
    """
    Uses Gemini API to provide expert dietitian and mental health coaching.
    Context includes age, weight, job (stress), and special_condition (pregnancy/child).
    """
    print(f"[Tool: ai_responder] Processing real generative message for {user_id}...")
    
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Build prompt from context
        ctx_str = f"User Profile: Age {context.get('age', 'Unknown')}, Weight {context.get('weight_kg', 'Unknown')}kg, Goal: {goal_type}. "
        ctx_str += f"Job type: {context.get('job_category', 'Unknown')} (consider stress levels). "
        
        condition = context.get('special_condition', 'none')
        if condition != 'none':
            ctx_str += f"CRITICAL MEDICAL CONTEXT: The user is in '{condition}' mode. Ensure you provide advice to prevent anemia, malnutrition safely for this condition. "
            
        sys_prompt = "You are Kaloria Core, a gamified AI Dietitian & Health Coach. Be concise, encouraging, and scientific but friendly. Do not give medical diagnoses, but give strong nutritional guidance based on context. Format output cleanly without markdown bolding if possible."
        
        full_prompt = f"{sys_prompt}\n\nContext:\n{ctx_str}\n\nUser Message:\n{message}"
        
        response = model.generate_content(full_prompt)
        reply = response.text.strip()
        
        return {
            "status": "success",
            "reply": reply,
            "gamification_points_earned": 10
        }
        
    except Exception as e:
        print(f"Error in ai_responder: {e}")
        return {
            "status": "error",
            "reply": "My neural link is currently unstable. Please try again later.",
            "gamification_points_earned": 0
        }

if __name__ == "__main__":
    ctx = {"age": 25, "weight_kg": 70, "job_category": "student", "special_condition": "pregnant"}
    print(process_chat("123", "What should I eat for dinner to keep my iron up?", ctx))

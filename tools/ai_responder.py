
import os

from dotenv import load_dotenv
from google import genai

from tools.gemini_fallback import generate_with_fallback


def _get_client():
    """Load the latest .env values and create a Gemini client."""
    load_dotenv()

    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY is missing")

    return genai.Client(
        api_key=api_key,
        http_options=genai.types.HttpOptions(timeout=60000),
    )


def process_chat(
    user_id: str,
    message: str,
    context: dict,
    goal_type: str = "health_focus"
):
    """
    Uses Gemini API to provide diet and health coaching.
    Context includes age, weight, job/stress information,
    and special condition.
    """

    print(
        f"[Tool: ai_responder] Processing real generative message "
        f"for {user_id}..."
    )

    condition = (context or {}).get("condition", "none") or "none"
    age = (context or {}).get("age", "unknown")
    weight = (context or {}).get("weight", "unknown")
    job = (context or {}).get("job", "unknown")

    try:
        client = _get_client()

        ctx_str = (
            f"User Profile: Age {age}, Weight {weight}kg, "
            f"Goal: {goal_type}. "
        )

        ctx_str += (
            f"Job type: {job} (consider stress levels). "
        )

        if condition != "none":
            ctx_str += (
                f"CRITICAL MEDICAL CONTEXT: The user is in "
                f"'{condition}' mode. Provide safe, general "
                f"nutritional guidance appropriate to this context. "
                f"Do not diagnose medical conditions. "
            )

        sys_prompt = (
            "You are Kaloria Core, a gamified AI Dietitian & "
            "Health Coach. Be concise, encouraging, scientific, "
            "and friendly. Do not give medical diagnoses. "
            "Give practical nutritional guidance based on the "
            "user's context. Format the response cleanly."
        )

        full_prompt = (
            f"{sys_prompt}\n\n"
            f"Context:\n{ctx_str}\n\n"
            f"User Message:\n{message}"
        )

        response = generate_with_fallback(client, full_prompt)

        reply = response.text.strip()

        return {
            "status": "success",
            "reply": reply,
            "gamification_points_earned": 10,
        }

    except Exception as e:
        print(f"Error in ai_responder: {e}")

        return {
            "status": "error",
            "reply": (
                "Sorry, the Diet Coach AI is temporarily unavailable "
                "(service busy or daily limit reached). "
                "Please try your question again in a little while."
            ),
            "gamification_points_earned": 0,
        }


if __name__ == "__main__":
    ctx = {
        "age": 25,
        "weight": 70,
        "job": "student",
        "condition": "pregnant"
    }

    print(
        process_chat(
            "123",
            "What should I eat for dinner to keep my iron up?",
            ctx
        )
    )


import base64
import os
import re
import uuid

from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

load_dotenv()

# Import the Navigation reasoning layer and specific tools as needed
from navigation import route_request
from tools.ai_responder import process_chat
from tools.food_detection import detect_food
from tools.calorie_estimator import estimate_calories
from tools.persistence import load_profile, save_food_log, save_profile, validate_password

app = FastAPI(title="Kaloria AI", description="End-to-end Backend Server powering Kaloria")

# Mount the static frontend directory
app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
def serve_dashboard():
    """Serve the interactive HTML dashboard."""
    return FileResponse("frontend/index.html")


# --- API ENDPOINTS ---

@app.post("/api/scan-food")
async def scan_food_endpoint(file: UploadFile = File(...)):
    """Receives the uploaded image (multipart field 'file') and returns detect_food() output directly."""
    print("[SCAN MEAL] Request received")
    print(f"[SCAN MEAL] Uploaded filename: {file.filename}")
    print(f"[SCAN MEAL] Content type: {file.content_type}")

    img_bytes = await file.read()
    if not img_bytes:
        return {"status": "error", "message": "No image uploaded."}

    os.makedirs(".tmp/food_images", exist_ok=True)
    suffix = os.path.splitext(file.filename or "")[1].lower()
    if suffix not in (".jpg", ".jpeg", ".png", ".webp"):
        suffix = ".jpg"
    temp_path = os.path.abspath(f".tmp/food_images/{uuid.uuid4().hex}{suffix}")

    try:
        with open(temp_path, "wb") as f:
            f.write(img_bytes)
        print(f"[SCAN MEAL] Temporary file: {temp_path}")
        print(f"[SCAN MEAL] File exists: {os.path.exists(temp_path)}")
        print("[SCAN MEAL] Calling detect_food(...)")
        result = await run_in_threadpool(detect_food, temp_path)
        print(f"[SCAN MEAL] Detector result: {result}")
    except Exception as exc:
        print(f"[SCAN MEAL] Exception: {exc}")
        return {"status": "error", "message": f"Scan failed: {exc}"}
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return result


class ManualLogRequest(BaseModel):
    food_name: str
    weight_g: int


@app.post("/api/estimate-food")
def estimate_food_endpoint(req: ManualLogRequest):
    result = estimate_calories(req.food_name, req.weight_g)
    return {"status": "success", "data": {"food_name": req.food_name, "calories": result.get("calories", 0)}}


class ProfileRequest(BaseModel):
    name: str
    email: str
    password: str
    age: int
    weight: int
    job: str = "desk_job"
    condition: str = "none"


@app.post("/api/auth/register")
def register_user(req: ProfileRequest):
    email = req.email.strip().lower()
    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        return {"status": "error", "message": "Enter a valid email address."}
    if not validate_password(req.password):
        return {"status": "error", "message": "Password must be at least 8 characters and include letters and numbers."}
    if load_profile(email):
        return {"status": "error", "message": "An account with this email already exists."}

    saved = save_profile(req.model_dump())
    profile = {**saved["profile"]}
    profile.pop("password", None)
    return {"status": "success", "data": profile}


class LoginRequest(BaseModel):
    email: str
    password: str


@app.post("/api/auth/login")
def login_user(req: LoginRequest):
    email = req.email.strip().lower()
    profile = load_profile(email)
    if not profile:
        return {"status": "error", "message": "No account found for this email."}

    if profile.get("password") != req.password:
        return {"status": "error", "message": "Incorrect password."}

    sanitized = {**profile}
    sanitized.pop("password", None)
    return {"status": "success", "data": sanitized}


@app.post("/api/auth/update-profile")
def update_user_profile(req: ProfileRequest):
    email = req.email.strip().lower()
    existing = load_profile(email)
    if not existing:
        return {"status": "error", "message": "Profile not found."}

    updated = save_profile(req.model_dump())
    profile = {**updated["profile"]}
    profile.pop("password", None)
    return {"status": "success", "data": profile}


class FoodEntryRequest(BaseModel):
    user_email: str
    food_name: str
    calories: int
    protein: int = 0
    carbs: int = 0
    fat: int = 0


@app.post("/api/food-log")
def save_food_entry(req: FoodEntryRequest):
    saved = save_food_log(req.model_dump())
    return {"status": "success", "data": saved}


class ChatRequest(BaseModel):
    user_message: str
    user_profile: dict


@app.post("/api/chat")
def chat_endpoint(req: ChatRequest):
    """Connects to AI Responder Toolkit"""
    result = process_chat(
        user_id=req.user_profile.get("name", "User"),
        message=req.user_message,
        context=req.user_profile,
        goal_type=req.user_profile.get("condition", "maintenance"),
    )
    return result


class DailyHealthRequest(BaseModel):
    user_id: str = "uuid-1234"
    daily_target: int = 2000


@app.post("/api/daily-health")
def daily_health_endpoint(req: DailyHealthRequest):
    payload = {"flow": "daily_health", "user_id": req.user_id, "daily_target": req.daily_target}
    result = route_request(payload)
    return {"status": "success", "data": result, "message": f"Successfully calculated health target for {req.user_id}"}


if __name__ == "__main__":
    print("🚀 Starting Kaloria AI Server...")
    print("🌍 View Dashboard at: http://localhost:8000")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

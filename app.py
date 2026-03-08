import base64
import os
import uuid
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn

# Import the Navigation reasoning layer and specific tools as needed
from navigation import route_request
from tools.ai_responder import process_chat
from tools.food_detection import detect_food
from tools.calorie_estimator import estimate_calories

app = FastAPI(title="Kaloria AI", description="End-to-end Backend Server powering Kaloria")

# Mount the static frontend directory
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def serve_dashboard():
    """Serve the interactive HTML dashboard."""
    return FileResponse("frontend/index.html")

# --- API ENDPOINTS ---

class FoodLogRequest(BaseModel):
    image_data: str # Base64 string

@app.post("/api/scan-food")
def scan_food_endpoint(req: FoodLogRequest):
    """Hits the Food Scan Navigation Flow (using direct tool call for simplicity here)"""
    # 1. Decode base64 to temp file
    header, encoded = req.image_data.split(",", 1) if "," in req.image_data else ("", req.image_data)
    img_bytes = base64.b64decode(encoded)
    
    os.makedirs(".tmp/food_images", exist_ok=True)
    temp_path = f".tmp/food_images/{uuid.uuid4().hex}.jpg"
    
    with open(temp_path, "wb") as f:
        f.write(img_bytes)
    
    # 2. Run architecture detection tool
    result = detect_food(temp_path)
    
    # 3. Clean up
    if os.path.exists(temp_path):
        os.remove(temp_path)
        
    return {"status": "success", "data": result}

class ManualLogRequest(BaseModel):
    food_name: str
    weight_g: int

@app.post("/api/estimate-food")
def estimate_food_endpoint(req: ManualLogRequest):
    result = estimate_calories(req.food_name, req.weight_g)
    return {"status": "success", "data": {"food_name": req.food_name, "calories": result.get("calories", 0)}}


class ChatRequest(BaseModel):
    user_message: str
    user_profile: dict

@app.post("/api/chat")
def chat_endpoint(req: ChatRequest):
    """Connects to AI Responder Toolkit"""
    # route_request can be used, but calling process_chat directly maps nicely for the REST endpoint
    result = process_chat(
        user_id=req.user_profile.get("name", "User"),
        message=req.user_message,
        context=req.user_profile,
        goal_type=req.user_profile.get("condition", "maintenance")
    )
    return result

class DailyHealthRequest(BaseModel):
    user_id: str = "uuid-1234"
    daily_target: int = 2000

@app.post("/api/daily-health")
def daily_health_endpoint(req: DailyHealthRequest):
    payload = {
        "flow": "daily_health",
        "user_id": req.user_id,
        "daily_target": req.daily_target
    }
    result = route_request(payload)
    return {"status": "success", "data": result, "message": f"Successfully calculated health target for {req.user_id}"}

if __name__ == "__main__":
    print("🚀 Starting Kaloria AI Server...")
    print("🌍 View Dashboard at: http://localhost:8000")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

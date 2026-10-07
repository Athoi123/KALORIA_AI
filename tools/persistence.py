import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / ".tmp"
PROFILES_PATH = DATA_DIR / "profiles.json"
FOOD_LOGS_PATH = DATA_DIR / "food_logs.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        content = path.read_text(encoding="utf-8")
        if not content.strip():
            return default
        return json.loads(content)
    except Exception:
        return default


def _write_json(path: Path, data: Any) -> None:
    _ensure_data_dir()
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _get_supabase_client():
    url = os.environ.get("SUPABASE_URL")
    key = (
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ.get("SUPABASE_KEY")
        or os.environ.get("SUPABASE_ANON_KEY")
    )
    if not url or not key:
        return None
    try:
        return create_client(url, key)
    except Exception:
        return None


def validate_password(password: str) -> bool:
    if len(password) < 8:
        return False
    if not re.search(r"[A-Za-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    return True


def build_profile_record(profile: Dict[str, Any]) -> Dict[str, Any]:
    email = str(profile.get("email", "")).strip().lower()
    record = {
        "user_id": profile.get("user_id") or str(uuid.uuid4()),
        "id": profile.get("id") or profile.get("user_id") or str(uuid.uuid4()),
        "name": profile.get("name", "User"),
        "email": email,
        "password": profile.get("password", ""),
        "age": int(profile.get("age", 0) or 0),
        "weight": int(profile.get("weight", 0) or 0),
        "job": profile.get("job", "desk_job"),
        "condition": profile.get("condition", "none"),
        "created_at": profile.get("created_at") or _utc_now(),
        "updated_at": _utc_now(),
    }
    return record


def save_profile(profile: Dict[str, Any]) -> Dict[str, Any]:
    record = build_profile_record(profile)
    email = record["email"]

    try:
        client = _get_supabase_client()
        if client and email:
            payload = {
                "id": record["id"],
                "email": email,
                "name": record["name"],
                "age": record["age"],
                "weight": record["weight"],
                "job": record["job"],
                "condition": record["condition"],
                "updated_at": record["updated_at"],
            }
            client.table("profiles").upsert(payload, on_conflict="email").execute()
            return {"success": True, "source": "supabase", "profile": record}
    except Exception:
        pass

    profiles = _read_json(PROFILES_PATH, {})
    if not isinstance(profiles, dict):
        profiles = {}
    profiles[email] = record
    _write_json(PROFILES_PATH, profiles)
    return {"success": True, "source": "local", "profile": record}


def load_profile(email: str) -> Optional[Dict[str, Any]]:
    email_key = str(email or "").strip().lower()
    if not email_key:
        return None

    try:
        client = _get_supabase_client()
        if client:
            result = client.table("profiles").select("*").eq("email", email_key).limit(1).execute()
            rows = getattr(result, "data", []) or []
            if rows:
                return rows[0]
    except Exception:
        pass

    profiles = _read_json(PROFILES_PATH, {})
    if isinstance(profiles, dict):
        return profiles.get(email_key)
    return None


def save_food_log(payload: Dict[str, Any]) -> Dict[str, Any]:
    log_entry = {
        "id": payload.get("id") or str(uuid.uuid4()),
        "user_email": str(payload.get("user_email", "")).strip().lower(),
        "food_name": payload.get("food_name", "Unknown Food"),
        "calories": int(payload.get("calories", 0) or 0),
        "protein": int(payload.get("protein", 0) or 0),
        "carbs": int(payload.get("carbs", 0) or 0),
        "fat": int(payload.get("fat", 0) or 0),
        "logged_at": payload.get("logged_at") or _utc_now(),
    }

    try:
        client = _get_supabase_client()
        if client and log_entry["user_email"]:
            client.table("food_logs").insert(log_entry).execute()
            return {"success": True, "source": "supabase", **log_entry}
    except Exception:
        pass

    logs = _read_json(FOOD_LOGS_PATH, [])
    if not isinstance(logs, list):
        logs = []
    logs.append(log_entry)
    _write_json(FOOD_LOGS_PATH, logs)
    return {"success": True, "source": "local", **log_entry}


def get_user_food_logs(email: str):
    email_key = str(email or "").strip().lower()
    if not email_key:
        return []

    try:
        client = _get_supabase_client()
        if client:
            result = client.table("food_logs").select("*").eq("user_email", email_key).execute()
            rows = getattr(result, "data", []) or []
            if rows:
                return rows
    except Exception:
        pass

    logs = _read_json(FOOD_LOGS_PATH, [])
    if not isinstance(logs, list):
        return []
    return [item for item in logs if str(item.get("user_email", "")).lower() == email_key]

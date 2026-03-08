import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def get_supabase_client() -> Client:
    url: str = os.environ.get("SUPABASE_URL", "")
    key: str = os.environ.get("SUPABASE_KEY", "")
    return create_client(url, key)

def calculate_daily_total(user_id: str) -> int:
    """
    Calculate total daily calories by querying Supabase.
    Input: user_id
    Output: daily calorie total (int)
    """
    print(f"[Tool: calorie_tracker] Calculating total for user: {user_id} via Supabase")
    
    try:
        supabase = get_supabase_client()
        # Mock assumption: table structure `food_logs` with a `calories` interior json or column
        # In actual implementation: supabase.table('food_logs').select('calories').eq('user_id', user_id).execute()
        # Returning sum for logic demo
        print("-> Querying Supabase `food_logs` table...")
        return 500  # Mocked result of query sum for architecture demo
    except Exception as e:
        print(f"Supabase connection error: {e}")
        return 0

if __name__ == "__main__":
    result = calculate_daily_total("uuid-1234")
    print(f"Total Daily Calories: {result}")

def calculate_rewards(daily_progress: dict) -> dict:
    """
    Calculate gamification rewards.
    Input: daily progress dict (e.g. {goal_met: bool, current_streak: int})
    Output: dict with coins, badges, streak updates
    """
    print("[Tool: reward_engine] Computing end-of-day rewards...")
    
    coins = 0
    badges = []
    streak = daily_progress.get("current_streak", 0)
    
    if daily_progress.get("goal_met"):
        coins += 10
        streak += 1
    else:
        streak = 0
        
    if streak >= 7:
        coins += 50
        badges.append("Healthy Week")
        
    return {
        "coins_earned": coins,
        "badges_awarded": badges,
        "new_streak": streak
    }

if __name__ == "__main__":
    result = calculate_rewards({"goal_met": True, "current_streak": 6})
    print(result)

def send_alert(trigger_event: str, message: str) -> bool:
    """
    Send alerts.
    Input: trigger event string, message
    Output: success boolean (push notification)
    """
    print(f"[Tool: notification_service] Sending {trigger_event} alert...")
    print(f"-> Payload: {message}")
    
    # Mocking push notification out to Firebase
    return True

if __name__ == "__main__":
    send_alert("meal_reminder", "Time for lunch!")

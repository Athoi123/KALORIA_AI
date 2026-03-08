# SOP: Notifications

## Goal
Defines alerts and messaging logic.

## Triggers
- calorie goal reached
- streak milestones
- health warnings
- meal reminders

## Outputs
- Push notification payload

## Logic
1. System event fires on trigger.
2. Construct payload and message body.
3. Send via Firebase Notification Key.

## Edge Cases
- User has disabled notifications in device settings.
- Late night notifications (respect "Do Not Disturb" hours).

## Security Rules
- Do not include sensitive health conditions in the plaintext push notification.

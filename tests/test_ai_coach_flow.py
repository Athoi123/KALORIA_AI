import unittest
from unittest.mock import patch

from navigation import process_ai_coach_flow


class NavigationAICoachTests(unittest.TestCase):
    @patch("navigation.process_chat", return_value={
        "status": "success",
        "reply": "A balanced plate with protein, fiber, and hydration is best after training.",
        "gamification_points_earned": 10,
    })
    def test_ai_coach_flow_uses_live_responder(self, mock_process_chat):
        payload = {
            "question": "What should I eat after training?",
            "user_id": "ava@example.com",
            "user_profile": {
                "name": "Ava",
                "age": 28,
                "weight": 62,
                "job": "desk_job",
                "condition": "none",
            },
        }

        result = process_ai_coach_flow(payload)

        self.assertEqual(result["status"], "success")
        self.assertEqual(
            result["ai_response"],
            "A balanced plate with protein, fiber, and hydration is best after training.",
        )
        mock_process_chat.assert_called_once()


if __name__ == "__main__":
    unittest.main()

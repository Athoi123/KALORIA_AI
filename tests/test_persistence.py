import json
import unittest
from pathlib import Path

from tools.persistence import save_profile, load_profile, save_food_log, build_profile_record


class PersistenceTests(unittest.TestCase):
    def setUp(self):
        self.profile = {
            "name": "Ava",
            "email": "ava@example.com",
            "password": "secret123",
            "age": 28,
            "weight": 62,
            "job": "desk_job",
            "condition": "none",
        }

    def test_profile_round_trip(self):
        save_profile(self.profile)
        loaded = load_profile("ava@example.com")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["name"], "Ava")
        self.assertEqual(loaded["email"], "ava@example.com")

    def test_food_log_saves_payload(self):
        payload = {
            "user_email": "ava@example.com",
            "food_name": "Chicken Salad",
            "calories": 420,
            "protein": 30,
            "carbs": 20,
            "fat": 18,
        }
        saved = save_food_log(payload)
        self.assertTrue(saved["success"])
        self.assertEqual(saved["food_name"], "Chicken Salad")

    def test_profile_record_includes_required_fields(self):
        record = build_profile_record(self.profile)
        self.assertIn("user_id", record)
        self.assertIn("email", record)
        self.assertIn("created_at", record)


if __name__ == "__main__":
    unittest.main()

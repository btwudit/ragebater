import unittest

import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1])
)

from app import app


class TestChatAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def test_health(self):
        response = self.client.get("/api/health")

        self.assertEqual(response.status_code, 200)

        data = response.get_json()

        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["service"], "RageBater API")

    def test_chat_success(self):
        response = self.client.post(
            "/api/chat",
            json={"message": "hello"},
        )

        self.assertEqual(response.status_code, 200)

        data = response.get_json()

        self.assertTrue(data["success"])
        self.assertIn("data", data)

        result = data["data"]

        required_keys = {
            "analysis",
            "strategy",
            "reason",
            "base_intensity",
            "personality",
            "intensity",
        }

        self.assertTrue(
            required_keys.issubset(result.keys())
        )

    def test_chat_missing_message(self):
        response = self.client.post(
            "/api/chat",
            json={},
        )

        self.assertEqual(response.status_code, 400)

        data = response.get_json()

        self.assertEqual(
            data["error"],
            "Message is required",
        )

    def test_chat_empty_message(self):
        response = self.client.post(
            "/api/chat",
            json={"message": "   "},
        )

        self.assertEqual(response.status_code, 400)

        data = response.get_json()

        self.assertEqual(
            data["error"],
            "Message cannot be empty",
        )

    def test_chat_non_string_message(self):
        response = self.client.post(
            "/api/chat",
            json={"message": 123},
        )

        self.assertEqual(response.status_code, 400)

        data = response.get_json()

        self.assertEqual(
            data["error"],
            "Message must be a string",
        )

    def test_chat_reset(self):
        response = self.client.post(
            "/api/chat/reset",
        )

        self.assertEqual(response.status_code, 200)

        data = response.get_json()

        self.assertTrue(data["success"])
        self.assertEqual(
            data["message"],
            "Personality reset successfully",
        )


if __name__ == "__main__":
    unittest.main()
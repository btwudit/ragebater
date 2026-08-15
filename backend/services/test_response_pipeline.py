import unittest

from backend.services.response_pipeline import ResponsePipeline


class TestResponsePipeline(unittest.TestCase):

    def setUp(self):
        self.pipeline = ResponsePipeline()

    def assert_valid_plan(self, result):
        required_keys = {
            "analysis",
            "strategy",
            "reason",
            "base_intensity",
            "personality",
            "intensity",
        }

        self.assertEqual(
            set(result.keys()),
            required_keys,
        )

        self.assertIsInstance(result["analysis"], dict)
        self.assertIsInstance(result["strategy"], str)
        self.assertIsInstance(result["reason"], str)

        self.assertIsInstance(
            result["base_intensity"],
            float,
        )

        self.assertIsInstance(
            result["personality"],
            dict,
        )

        self.assertIsInstance(
            result["intensity"],
            float,
        )

        self.assertGreaterEqual(
            result["base_intensity"],
            0.0,
        )

        self.assertLessEqual(
            result["base_intensity"],
            1.0,
        )

        self.assertGreaterEqual(
            result["intensity"],
            0.0,
        )

        self.assertLessEqual(
            result["intensity"],
            1.0,
        )

    def test_hello_message(self):
        result = self.pipeline.process("hello")

        self.assertEqual(
            result["analysis"]["intent"],
            "greeting",
        )

        self.assertEqual(
            result["strategy"],
            "playful_sarcasm",
        )

        self.assert_valid_plan(result)

    def test_python_question(self):
        result = self.pipeline.process(
            "How does Python work?"
        )

        self.assertEqual(
            result["analysis"]["topic"],
            "python",
        )

        self.assertEqual(
            result["analysis"]["intent"],
            "question",
        )

        self.assert_valid_plan(result)

    def test_confident_user(self):
        result = self.pipeline.process(
            "Python is obviously easy"
        )

        self.assertEqual(
            result["analysis"]["emotion"],
            "confident",
        )

        self.assertEqual(
            result["strategy"],
            "competitive_teasing",
        )

        self.assertGreater(
            result["intensity"],
            0.0,
        )

        self.assert_valid_plan(result)

    def test_frustrated_user(self):
        result = self.pipeline.process(
            "why isn't my code working?"
        )

        self.assertEqual(
            result["analysis"]["emotion"],
            "frustrated",
        )

        self.assertEqual(
            result["strategy"],
            "calm_support",
        )

        self.assertLess(
            result["intensity"],
            result["base_intensity"],
        )

        self.assert_valid_plan(result)

    def test_hostile_user(self):
        result = self.pipeline.process(
            "this code is stupid and useless"
        )

        self.assertGreater(
            result["analysis"]["hostility_level"],
            0.0,
        )

        self.assertEqual(
            result["strategy"],
            "reverse_psychology",
        )

        self.assert_valid_plan(result)

    def test_positive_user(self):
        result = self.pipeline.process(
            "I love this"
        )

        self.assertEqual(
            result["analysis"]["emotion"],
            "positive",
        )

        self.assertEqual(
            result["strategy"],
            "ego_boost",
        )

        self.assert_valid_plan(result)

    def test_personality_changes_between_messages(self):
        first = self.pipeline.process(
            "Python is obviously easy"
        )

        first_confidence = first["personality"]["confidence"]

        second = self.pipeline.process(
            "Python is obviously easy"
        )

        second_confidence = second["personality"]["confidence"]

        self.assertGreater(
            second_confidence,
            first_confidence,
        )

    def test_reset_personality(self):
        self.pipeline.process(
            "Python is obviously easy"
        )

        state_after_reset = (
            self.pipeline.reset_personality()
        )

        self.assertEqual(
            state_after_reset,
            {
                "confidence": 0.60,
                "aggression": 0.35,
                "playfulness": 0.55,
                "irritation": 0.20,
            },
        )

    def test_empty_message_rejected(self):
        with self.assertRaises(ValueError):
            self.pipeline.process("")

    def test_whitespace_message_rejected(self):
        with self.assertRaises(ValueError):
            self.pipeline.process("   ")

    def test_non_string_message_rejected(self):
        with self.assertRaises(TypeError):
            self.pipeline.process(123)


if __name__ == "__main__":
    unittest.main()
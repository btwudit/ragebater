import unittest

from backend.services.analysis_service import analyze_message


class TestAnalysisService(unittest.TestCase):

    def assert_valid_analysis(self, result):
        required_keys = {
            "intent",
            "emotion",
            "topic",
            "challenge_level",
            "hostility_level",
            "confidence",
        }

        self.assertEqual(set(result.keys()), required_keys)

        self.assertIsInstance(result["intent"], str)
        self.assertIsInstance(result["emotion"], str)
        self.assertIsInstance(result["topic"], str)

        self.assertIsInstance(result["challenge_level"], float)
        self.assertIsInstance(result["hostility_level"], float)
        self.assertIsInstance(result["confidence"], float)

        self.assertGreaterEqual(result["challenge_level"], 0.0)
        self.assertLessEqual(result["challenge_level"], 1.0)

        self.assertGreaterEqual(result["hostility_level"], 0.0)
        self.assertLessEqual(result["hostility_level"], 1.0)

        self.assertGreaterEqual(result["confidence"], 0.0)
        self.assertLessEqual(result["confidence"], 1.0)

    def test_greeting(self):
        result = analyze_message("hello")

        self.assertEqual(result["intent"], "greeting")
        self.assertEqual(result["emotion"], "neutral")

        self.assert_valid_analysis(result)

    def test_python_question(self):
        result = analyze_message(
            "How does Python work?"
        )

        self.assertEqual(result["intent"], "question")
        self.assertEqual(result["topic"], "python")

        self.assert_valid_analysis(result)

    def test_confident_python_statement(self):
        result = analyze_message(
            "Python is obviously easy"
        )

        self.assertEqual(result["emotion"], "confident")
        self.assertEqual(result["topic"], "python")

        self.assertGreaterEqual(
            result["challenge_level"],
            0.55,
        )

        self.assertGreater(
            result["confidence"],
            0.5,
        )

        self.assert_valid_analysis(result)

    def test_frustrated_question(self):
        result = analyze_message(
            "why isn't my code working?"
        )

        self.assertEqual(result["intent"], "question")
        self.assertEqual(result["emotion"], "frustrated")

        self.assert_valid_analysis(result)

    def test_hostile_statement(self):
        result = analyze_message(
            "this code is stupid and useless"
        )

        self.assertGreater(
            result["hostility_level"],
            0.0,
        )

        self.assert_valid_analysis(result)

    def test_positive_message(self):
        result = analyze_message(
            "I love this project"
        )

        self.assertEqual(
            result["emotion"],
            "positive",
        )

        self.assert_valid_analysis(result)

    def test_robotics_command(self):
        result = analyze_message(
            "move the robot arm forward"
        )

        self.assertEqual(
            result["topic"],
            "robotics",
        )

        self.assert_valid_analysis(result)

    def test_general_message(self):
        result = analyze_message(
            "The weather is interesting today."
        )

        self.assert_valid_analysis(result)

    def test_non_string_input(self):
        with self.assertRaises(TypeError):
            analyze_message(123)


if __name__ == "__main__":
    unittest.main()
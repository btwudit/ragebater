import unittest

from backend.engine.rage_engine import STRATEGIES, select_strategy


def make_analysis(
    intent="statement",
    emotion="neutral",
    topic="general",
    challenge_level=0.2,
    hostility_level=0.0,
    confidence=0.8,
):
    return {
        "intent": intent,
        "emotion": emotion,
        "topic": topic,
        "challenge_level": challenge_level,
        "hostility_level": hostility_level,
        "confidence": confidence,
    }


class TestRageEngine(unittest.TestCase):

    def assert_valid_result(self, result):
        self.assertIn("strategy", result)
        self.assertIn("intensity", result)
        self.assertIn("reason", result)

        self.assertIn(result["strategy"], STRATEGIES)

        self.assertIsInstance(result["intensity"], float)
        self.assertGreaterEqual(result["intensity"], 0.0)
        self.assertLessEqual(result["intensity"], 1.0)

        self.assertIsInstance(result["reason"], str)
        self.assertTrue(result["reason"])

    def test_frustrated_user_gets_calm_support(self):
        analysis = make_analysis(
            emotion="frustrated",
            challenge_level=0.5,
        )

        result = select_strategy(analysis)

        self.assertEqual(result["strategy"], "calm_support")
        self.assertLessEqual(result["intensity"], 0.35)
        self.assert_valid_result(result)

    def test_confident_user_gets_competitive_teasing(self):
        analysis = make_analysis(
            emotion="confident",
            challenge_level=0.75,
        )

        result = select_strategy(analysis)

        self.assertEqual(result["strategy"], "competitive_teasing")
        self.assertGreaterEqual(result["intensity"], 0.60)
        self.assert_valid_result(result)

    def test_high_hostility_gets_reverse_psychology(self):
        analysis = make_analysis(
            emotion="negative",
            challenge_level=0.8,
            hostility_level=0.8,
        )

        result = select_strategy(analysis)

        self.assertEqual(result["strategy"], "reverse_psychology")
        self.assertGreaterEqual(result["intensity"], 0.65)
        self.assert_valid_result(result)

    def test_playful_user_gets_playful_sarcasm(self):
        analysis = make_analysis(
            emotion="playful",
            challenge_level=0.4,
        )

        result = select_strategy(analysis)

        self.assertEqual(result["strategy"], "playful_sarcasm")
        self.assert_valid_result(result)

    def test_positive_user_gets_ego_boost(self):
        analysis = make_analysis(
            emotion="positive",
            challenge_level=0.2,
        )

        result = select_strategy(analysis)

        self.assertEqual(result["strategy"], "ego_boost")
        self.assert_valid_result(result)

    def test_greeting_gets_playful_sarcasm(self):
        analysis = make_analysis(
            intent="greeting",
            emotion="neutral",
        )

        result = select_strategy(analysis)

        self.assertEqual(result["strategy"], "playful_sarcasm")
        self.assert_valid_result(result)

    def test_neutral_input_gets_neutral_response(self):
        analysis = make_analysis()

        result = select_strategy(analysis)

        self.assertEqual(result["strategy"], "neutral_response")
        self.assert_valid_result(result)

    def test_missing_analysis_field_raises_error(self):
        analysis = make_analysis()
        del analysis["emotion"]

        with self.assertRaises(ValueError):
            select_strategy(analysis)

    def test_intensity_is_always_bounded(self):
        analysis = make_analysis(
            emotion="confident",
            challenge_level=1.0,
            hostility_level=1.0,
        )

        result = select_strategy(analysis)

        self.assertGreaterEqual(result["intensity"], 0.0)
        self.assertLessEqual(result["intensity"], 1.0)

    def test_all_results_have_expected_structure(self):
        analyses = [
            make_analysis(emotion="frustrated"),
            make_analysis(emotion="confident", challenge_level=0.8),
            make_analysis(
                emotion="negative",
                challenge_level=0.8,
                hostility_level=0.9,
            ),
            make_analysis(emotion="playful"),
            make_analysis(emotion="positive"),
            make_analysis(intent="greeting"),
            make_analysis(),
        ]

        for analysis in analyses:
            with self.subTest(analysis=analysis):
                result = select_strategy(analysis)
                self.assert_valid_result(result)


if __name__ == "__main__":
    unittest.main()
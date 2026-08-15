import unittest

from backend.engine.intensity_controller import calculate_intensity


DEFAULT_STATE = {
    "confidence": 0.60,
    "aggression": 0.35,
    "playfulness": 0.55,
    "irritation": 0.20,
}


class TestIntensityController(unittest.TestCase):

    def test_normal_intensity(self):
        result = calculate_intensity(
            base_intensity=0.50,
            personality_state=DEFAULT_STATE,
            emotion="neutral",
        )

        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0.0)
        self.assertLessEqual(result, 1.0)

    def test_frustrated_user_gets_lower_intensity(self):
        normal = calculate_intensity(
            base_intensity=0.70,
            personality_state=DEFAULT_STATE,
            emotion="neutral",
        )

        frustrated = calculate_intensity(
            base_intensity=0.70,
            personality_state=DEFAULT_STATE,
            emotion="frustrated",
        )

        self.assertLess(
            frustrated,
            normal,
        )

    def test_positive_user_gets_slightly_lower_intensity(self):
        normal = calculate_intensity(
            base_intensity=0.60,
            personality_state=DEFAULT_STATE,
            emotion="neutral",
        )

        positive = calculate_intensity(
            base_intensity=0.60,
            personality_state=DEFAULT_STATE,
            emotion="positive",
        )

        self.assertLess(
            positive,
            normal,
        )

    def test_high_aggression_increases_intensity(self):
        low_aggression = calculate_intensity(
            base_intensity=0.50,
            personality_state={
                "confidence": 0.60,
                "aggression": 0.10,
                "playfulness": 0.55,
                "irritation": 0.20,
            },
            emotion="neutral",
        )

        high_aggression = calculate_intensity(
            base_intensity=0.50,
            personality_state={
                "confidence": 0.60,
                "aggression": 0.90,
                "playfulness": 0.55,
                "irritation": 0.20,
            },
            emotion="neutral",
        )

        self.assertGreater(
            high_aggression,
            low_aggression,
        )

    def test_intensity_never_exceeds_one(self):
        result = calculate_intensity(
            base_intensity=1.0,
            personality_state={
                "confidence": 1.0,
                "aggression": 1.0,
                "playfulness": 1.0,
                "irritation": 1.0,
            },
            emotion="neutral",
        )

        self.assertLessEqual(result, 1.0)

    def test_intensity_never_goes_below_zero(self):
        result = calculate_intensity(
            base_intensity=0.0,
            personality_state={
                "confidence": 0.0,
                "aggression": 0.0,
                "playfulness": 0.0,
                "irritation": 0.0,
            },
            emotion="frustrated",
        )

        self.assertGreaterEqual(result, 0.0)


if __name__ == "__main__":
    unittest.main()
import unittest

from backend.engine.personality_state import (
    DEFAULT_STATE,
    PersonalityState,
)


class TestPersonalityState(unittest.TestCase):

    def assert_valid_state(self, state):
        expected_keys = {
            "confidence",
            "aggression",
            "playfulness",
            "irritation",
        }

        self.assertEqual(set(state.keys()), expected_keys)

        for key, value in state.items():
            self.assertIsInstance(value, float)
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_default_state(self):
        personality = PersonalityState()

        state = personality.get_state()

        self.assertEqual(
            state,
            {
                "confidence": 0.60,
                "aggression": 0.35,
                "playfulness": 0.55,
                "irritation": 0.20,
            },
        )

        self.assert_valid_state(state)

    def test_custom_initial_state(self):
        personality = PersonalityState(
            {
                "confidence": 0.8,
                "aggression": 0.2,
                "playfulness": 0.7,
                "irritation": 0.1,
            }
        )

        state = personality.get_state()

        self.assertEqual(state["confidence"], 0.8)
        self.assertEqual(state["aggression"], 0.2)
        self.assertEqual(state["playfulness"], 0.7)
        self.assertEqual(state["irritation"], 0.1)

        self.assert_valid_state(state)

    def test_update(self):
        personality = PersonalityState()

        state = personality.update(
            confidence_delta=0.1,
            aggression_delta=0.1,
            playfulness_delta=-0.1,
            irritation_delta=0.1,
        )

        self.assertEqual(state["confidence"], 0.70)
        self.assertEqual(state["aggression"], 0.45)
        self.assertEqual(state["playfulness"], 0.45)
        self.assertEqual(state["irritation"], 0.30)

        self.assert_valid_state(state)

    def test_values_are_clamped(self):
        personality = PersonalityState()

        state = personality.update(
            confidence_delta=10.0,
            aggression_delta=10.0,
            playfulness_delta=10.0,
            irritation_delta=10.0,
        )

        for value in state.values():
            self.assertEqual(value, 1.0)

        state = personality.update(
            confidence_delta=-10.0,
            aggression_delta=-10.0,
            playfulness_delta=-10.0,
            irritation_delta=-10.0,
        )

        for value in state.values():
            self.assertEqual(value, 0.0)

    def test_reset(self):
        personality = PersonalityState()

        personality.update(
            confidence_delta=0.2,
            aggression_delta=0.2,
            playfulness_delta=0.2,
            irritation_delta=0.2,
        )

        personality.reset()

        self.assertEqual(
            personality.get_state(),
            DEFAULT_STATE,
        )

    def test_confident_analysis(self):
        personality = PersonalityState()

        before = personality.get_state()

        after = personality.apply_analysis(
            {
                "emotion": "confident",
                "challenge_level": 0.8,
                "hostility_level": 0.0,
            }
        )

        self.assertGreater(
            after["confidence"],
            before["confidence"],
        )

        self.assertGreater(
            after["aggression"],
            before["aggression"],
        )

        self.assert_valid_state(after)

    def test_playful_analysis(self):
        personality = PersonalityState()

        before = personality.get_state()

        after = personality.apply_analysis(
            {
                "emotion": "playful",
                "challenge_level": 0.3,
                "hostility_level": 0.0,
            }
        )

        self.assertGreater(
            after["playfulness"],
            before["playfulness"],
        )

        self.assert_valid_state(after)

    def test_frustrated_analysis_reduces_aggression(self):
        personality = PersonalityState()

        before = personality.get_state()

        after = personality.apply_analysis(
            {
                "emotion": "frustrated",
                "challenge_level": 0.2,
                "hostility_level": 0.0,
            }
        )

        self.assertLess(
            after["aggression"],
            before["aggression"],
        )

        self.assertGreater(
            after["irritation"],
            before["irritation"],
        )

        self.assert_valid_state(after)

    def test_missing_analysis_fields(self):
        personality = PersonalityState()

        with self.assertRaises(ValueError):
            personality.apply_analysis(
                {
                    "emotion": "confident",
                }
            )

    def test_state_instances_are_independent(self):
        first = PersonalityState()
        second = PersonalityState()

        first.update(confidence_delta=0.2)

        self.assertNotEqual(
            first.get_state()["confidence"],
            second.get_state()["confidence"],
        )


if __name__ == "__main__":
    unittest.main()
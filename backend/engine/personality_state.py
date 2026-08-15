"""
RageBater Personality State.

Maintains the current emotional/personality state of RageBater.
This version is intentionally in-memory and deterministic.

Database persistence will be added later.
"""


DEFAULT_STATE = {
    "confidence": 0.60,
    "aggression": 0.35,
    "playfulness": 0.55,
    "irritation": 0.20,
}


def _clamp(
    value: float,
    minimum: float = 0.0,
    maximum: float = 1.0,
) -> float:
    """Keep a value between minimum and maximum."""
    return max(minimum, min(value, maximum))


class PersonalityState:
    """
    In-memory personality state for RageBater.

    Each instance owns its own state.
    """

    def __init__(self, initial_state=None):
        if initial_state is None:
            initial_state = DEFAULT_STATE

        self._state = {
            "confidence": float(initial_state["confidence"]),
            "aggression": float(initial_state["aggression"]),
            "playfulness": float(initial_state["playfulness"]),
            "irritation": float(initial_state["irritation"]),
        }

        self._clamp_state()

    def _clamp_state(self):
        """Ensure every state value stays between 0.0 and 1.0."""
        for key in self._state:
            self._state[key] = round(
                _clamp(self._state[key]),
                2,
            )

    def get_state(self) -> dict:
        """Return a copy of the current personality state."""
        return dict(self._state)

    def reset(self):
        """Reset the personality to its default state."""
        self._state = dict(DEFAULT_STATE)
        self._clamp_state()

    def update(
        self,
        confidence_delta: float = 0.0,
        aggression_delta: float = 0.0,
        playfulness_delta: float = 0.0,
        irritation_delta: float = 0.0,
    ) -> dict:
        """
        Apply changes to the personality state.

        All values are clamped to 0.0-1.0.
        """

        self._state["confidence"] += confidence_delta
        self._state["aggression"] += aggression_delta
        self._state["playfulness"] += playfulness_delta
        self._state["irritation"] += irritation_delta

        self._clamp_state()

        return self.get_state()

    def apply_analysis(self, analysis: dict) -> dict:
        """
        Update personality based on Input Analyzer output.

        This does not generate a response.
        It only adjusts internal personality state.
        """

        required_keys = {
            "emotion",
            "challenge_level",
            "hostility_level",
        }

        missing_keys = required_keys - analysis.keys()

        if missing_keys:
            missing = ", ".join(sorted(missing_keys))
            raise ValueError(f"Missing analysis fields: {missing}")

        emotion = analysis["emotion"]
        challenge = _clamp(float(analysis["challenge_level"]))
        hostility = _clamp(float(analysis["hostility_level"]))

        confidence_delta = 0.0
        aggression_delta = 0.0
        playfulness_delta = 0.0
        irritation_delta = 0.0

        if emotion == "confident":
            confidence_delta += 0.05
            aggression_delta += 0.05

        elif emotion == "playful":
            playfulness_delta += 0.08

        elif emotion == "positive":
            confidence_delta += 0.03
            playfulness_delta += 0.03

        elif emotion == "frustrated":
            irritation_delta += 0.05
            aggression_delta -= 0.08

        elif emotion == "negative":
            irritation_delta += 0.03
            aggression_delta += 0.03

        aggression_delta += challenge * 0.05
        irritation_delta += hostility * 0.05

        return self.update(
            confidence_delta=confidence_delta,
            aggression_delta=aggression_delta,
            playfulness_delta=playfulness_delta,
            irritation_delta=irritation_delta,
        )
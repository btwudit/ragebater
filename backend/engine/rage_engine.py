"""
RageBater Rage Engine.

The Rage Engine converts structured message analysis into a response
strategy. It does not generate the final response and does not call
an external AI service.

This is intentionally deterministic so the personality logic can be
tested independently before LLM integration.
"""


STRATEGIES = {
    "playful_sarcasm",
    "competitive_teasing",
    "reverse_psychology",
    "ego_boost",
    "calm_support",
    "neutral_response",
}


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    """Keep a numeric value inside the allowed range."""
    return max(minimum, min(value, maximum))


def _select_strategy(
    intent: str,
    emotion: str,
    challenge_level: float,
    hostility_level: float,
) -> str:
    """
    Select the response strategy based on analyzed user behavior.

    Priority is intentional:
    1. Frustrated users should not receive aggressive teasing.
    2. Hostile/challenging users can receive competitive responses.
    3. Playful/confident users can receive teasing.
    4. Positive users can receive an ego boost.
    5. Everything else gets a neutral response.
    """

    if emotion == "frustrated":
        return "calm_support"

    if hostility_level >= 0.70:
        return "reverse_psychology"

    if challenge_level >= 0.55 and emotion == "confident":
        return "competitive_teasing"

    if challenge_level >= 0.55 and hostility_level > 0:
        return "competitive_teasing"

    if emotion == "playful":
        return "playful_sarcasm"

    if emotion == "positive":
        return "ego_boost"

    if intent == "greeting":
        return "playful_sarcasm"

    return "neutral_response"


def _calculate_intensity(
    strategy: str,
    challenge_level: float,
    hostility_level: float,
    emotion: str,
) -> float:
    """Calculate response intensity between 0.0 and 1.0."""

    intensity = 0.35

    if strategy == "playful_sarcasm":
        intensity = 0.50 + challenge_level * 0.20

    elif strategy == "competitive_teasing":
        intensity = 0.60 + challenge_level * 0.30

    elif strategy == "reverse_psychology":
        intensity = 0.65 + hostility_level * 0.25

    elif strategy == "ego_boost":
        intensity = 0.40

    elif strategy == "calm_support":
        intensity = 0.20

    elif strategy == "neutral_response":
        intensity = 0.30

    # Frustrated users should always receive a lower intensity.
    if emotion == "frustrated":
        intensity -= 0.15

    return round(_clamp(intensity), 2)


def select_strategy(analysis: dict) -> dict:
    """
    Select a RageBater response strategy from message analysis.

    Expected analysis structure:

    {
        "intent": str,
        "emotion": str,
        "topic": str,
        "challenge_level": float,
        "hostility_level": float,
        "confidence": float
    }

    Returns:

    {
        "strategy": str,
        "intensity": float,
        "reason": str
    }
    """

    required_keys = {
        "intent",
        "emotion",
        "topic",
        "challenge_level",
        "hostility_level",
        "confidence",
    }

    missing_keys = required_keys - analysis.keys()

    if missing_keys:
        missing = ", ".join(sorted(missing_keys))
        raise ValueError(f"Missing analysis fields: {missing}")

    challenge_level = _clamp(float(analysis["challenge_level"]))
    hostility_level = _clamp(float(analysis["hostility_level"]))

    strategy = _select_strategy(
        intent=analysis["intent"],
        emotion=analysis["emotion"],
        challenge_level=challenge_level,
        hostility_level=hostility_level,
    )

    intensity = _calculate_intensity(
        strategy=strategy,
        challenge_level=challenge_level,
        hostility_level=hostility_level,
        emotion=analysis["emotion"],
    )

    reasons = {
        "playful_sarcasm": "The user appears playful and can handle light teasing.",
        "competitive_teasing": "The user shows confidence or competitive challenge.",
        "reverse_psychology": "The user's hostility is high enough for a stronger strategic response.",
        "ego_boost": "The user is positive, so the response should reinforce that energy.",
        "calm_support": "The user appears frustrated, so intensity should be reduced.",
        "neutral_response": "The input does not strongly indicate another response strategy.",
    }

    return {
        "strategy": strategy,
        "intensity": intensity,
        "reason": reasons[strategy],
    }
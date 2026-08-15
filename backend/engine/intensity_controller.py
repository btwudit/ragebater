"""
RageBater Intensity Controller.

Controls the final personality intensity based on strategy,
personality state, and user emotional condition.
"""


def _clamp(
    value: float,
    minimum: float = 0.0,
    maximum: float = 1.0,
) -> float:
    """Keep a value inside the allowed range."""
    return max(minimum, min(value, maximum))


def calculate_intensity(
    base_intensity: float,
    personality_state: dict,
    emotion: str,
) -> float:
    """
    Calculate final response intensity.

    The controller prevents frustrated users from receiving
    unnecessarily aggressive responses.
    """

    intensity = float(base_intensity)

    aggression = float(
        personality_state.get("aggression", 0.35)
    )

    playfulness = float(
        personality_state.get("playfulness", 0.55)
    )

    irritation = float(
        personality_state.get("irritation", 0.20)
    )

    # Personality influences the response.
    intensity += aggression * 0.10
    intensity += playfulness * 0.05
    intensity += irritation * 0.03

    # Frustrated users receive a significant intensity reduction.
    if emotion == "frustrated":
        intensity -= 0.25

    # Positive users should not automatically receive aggressive responses.
    elif emotion == "positive":
        intensity -= 0.05

    return round(_clamp(intensity), 2)
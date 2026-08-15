"""
RageBater Response Adapter
==========================

Converts the deterministic backend decision produced by
ResponsePipeline into a structured character command that
the frontend can render.

This module does NOT:
    - analyze user messages
    - calculate personality
    - calculate intensity
    - call an external AI service

Those responsibilities remain inside the existing backend
architecture.

The adapter only converts:

    strategy
    analysis
    personality
    intensity

into:

    response
    face
    gesture
    animation
    sticker
    delay_ms
    chaos_level
"""


from __future__ import annotations

from typing import Any


# ============================================================
# DEFAULTS
# ============================================================

DEFAULT_RESPONSE = (
    "Interesting take. But I think you're going to have "
    "to defend that one."
)

DEFAULT_FACE = "neutral"
DEFAULT_GESTURE = "idle"
DEFAULT_ANIMATION = "none"
DEFAULT_STICKER = "really"
DEFAULT_DELAY_MS = 700


# ============================================================
# STRATEGY RESPONSE DEFINITIONS
# ============================================================

STRATEGY_RESPONSES = {
    "playful_sarcasm": {
        "response": (
            "Oh, hello. Prepared to lose this argument? "
            "I hope so."
        ),
        "face": "smirk",
        "gesture": "point",
        "animation": "bounce",
        "sticker": "you_sure",
        "delay_ms": 700,
    },

    "neutral_response": {
        "response": (
            "Interesting. That's a claim. Now give me "
            "something worth arguing about."
        ),
        "face": "neutral",
        "gesture": "shrug",
        "animation": "none",
        "sticker": "really",
        "delay_ms": 700,
    },

    "challenge": {
        "response": (
            "That's a bold claim. Go on then. "
            "Try to prove it."
        ),
        "face": "smirk",
        "gesture": "point",
        "animation": "pulse",
        "sticker": "you_sure",
        "delay_ms": 800,
    },

    "aggressive_challenge": {
        "response": (
            "You really want to challenge me on that? "
            "Fine. Let's see what you've got."
        ),
        "face": "annoyed",
        "gesture": "point",
        "animation": "shake",
        "sticker": "nah_bro",
        "delay_ms": 850,
    },

    "deescalate": {
        "response": (
            "Alright, alright. Let's keep this debate "
            "under control."
        ),
        "face": "deadpan",
        "gesture": "stop",
        "animation": "none",
        "sticker": "really",
        "delay_ms": 750,
    },
}


# ============================================================
# INTENSITY HELPERS
# ============================================================

def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    """Clamp a numeric value to a safe range."""

    return max(minimum, min(maximum, float(value)))


def intensity_to_chaos(intensity: float) -> int:
    """
    Convert backend intensity (0.0-1.0) into the frontend
    chaos meter range (0-100).
    """

    normalized = clamp(intensity)

    return round(normalized * 100)


def calculate_delay(intensity: float, base_delay: int) -> int:
    """
    Slightly reduce response delay as intensity increases.

    Higher intensity:
        -> faster response

    Lower intensity:
        -> slightly slower response
    """

    normalized = clamp(intensity)

    reduction = round(normalized * 150)

    return max(450, base_delay - reduction)


# ============================================================
# PERSONALITY → VISUAL STATE
# ============================================================

def determine_face(
    strategy: str,
    intensity: float,
    personality: dict[str, Any],
) -> str:
    """
    Determine the character's facial expression.

    Strategy is considered first, then intensity and
    personality are used as fallbacks.
    """

    if strategy == "aggressive_challenge":
        return "annoyed"

    if strategy == "deescalate":
        return "deadpan"

    if strategy == "playful_sarcasm":
        return "smirk"

    if intensity >= 0.8:
        return "rage"

    aggression = float(personality.get("aggression", 0.0))
    playfulness = float(personality.get("playfulness", 0.0))

    if aggression >= 0.7:
        return "annoyed"

    if playfulness >= 0.65:
        return "smirk"

    return "neutral"


def determine_gesture(
    strategy: str,
    intensity: float,
) -> str:
    """Determine the character's hand gesture."""

    if strategy == "playful_sarcasm":
        return "point"

    if strategy == "aggressive_challenge":
        return "point"

    if strategy == "challenge":
        return "point"

    if strategy == "deescalate":
        return "stop"

    if intensity >= 0.75:
        return "clap"

    if intensity >= 0.5:
        return "shrug"

    return "idle"


def determine_animation(
    strategy: str,
    intensity: float,
) -> str:
    """Determine the character animation."""

    if strategy == "playful_sarcasm":
        return "bounce"

    if strategy == "aggressive_challenge":
        return "shake"

    if strategy == "challenge":
        return "pulse"

    if intensity >= 0.8:
        return "shake"

    if intensity >= 0.6:
        return "bounce"

    return "none"


# ============================================================
# MAIN ADAPTER
# ============================================================

def build_character_response(
    pipeline_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Convert a ResponsePipeline result into a frontend-ready
    RageBater character response.

    The original pipeline data is preserved.

    Additional fields:

        response
        face
        gesture
        animation
        sticker
        delay_ms
        chaos_level
    """

    if not isinstance(pipeline_result, dict):
        raise TypeError("pipeline_result must be a dictionary")

    strategy = str(
        pipeline_result.get(
            "strategy",
            "neutral_response",
        )
    )

    intensity = clamp(
        float(
            pipeline_result.get(
                "intensity",
                0.5,
            )
        )
    )

    personality = pipeline_result.get(
        "personality",
        {},
    )

    if not isinstance(personality, dict):
        personality = {}

    strategy_config = STRATEGY_RESPONSES.get(
        strategy,
        {},
    )

    response_text = strategy_config.get(
        "response",
        DEFAULT_RESPONSE,
    )

    base_delay = int(
        strategy_config.get(
            "delay_ms",
            DEFAULT_DELAY_MS,
        )
    )

    face = strategy_config.get(
        "face",
        determine_face(
            strategy,
            intensity,
            personality,
        ),
    )

    gesture = strategy_config.get(
        "gesture",
        determine_gesture(
            strategy,
            intensity,
        ),
    )

    animation = strategy_config.get(
        "animation",
        determine_animation(
            strategy,
            intensity,
        ),
    )

    sticker = strategy_config.get(
        "sticker",
        DEFAULT_STICKER,
    )

    delay_ms = calculate_delay(
        intensity,
        base_delay,
    )

    chaos_level = intensity_to_chaos(
        intensity,
    )

    # Preserve every field produced by ResponsePipeline.
    result = dict(pipeline_result)

    # Add frontend character commands.
    result.update(
        {
            "response": response_text,
            "face": face,
            "gesture": gesture,
            "animation": animation,
            "sticker": sticker,
            "delay_ms": delay_ms,
            "chaos_level": chaos_level,
        }
    )

    return result
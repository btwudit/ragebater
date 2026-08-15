"""
RageBater Response Adapter
==========================

Converts the decision produced by ResponsePipeline into a
frontend-ready RageBater character command.

The adapter does not analyze messages itself. It uses the
analysis already produced by the backend and converts that
decision into:

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
    "Alright, make your case. I'm listening."
)

DEFAULT_FACE = "neutral"
DEFAULT_GESTURE = "idle"
DEFAULT_ANIMATION = "none"
DEFAULT_STICKER = None
DEFAULT_DELAY_MS = 650


# ============================================================
# HELPERS
# ============================================================

def clamp(
    value: float,
    minimum: float = 0.0,
    maximum: float = 1.0,
) -> float:
    """Keep a numeric value inside a safe range."""

    return max(
        minimum,
        min(maximum, float(value)),
    )


def chaos_from_intensity(intensity: float) -> int:
    """Convert 0.0-1.0 intensity into 0-100 chaos."""

    return round(clamp(intensity) * 100)


def calculate_delay(
    intensity: float,
    base_delay: int,
) -> int:
    """Higher intensity produces a slightly faster response."""

    reduction = round(clamp(intensity) * 120)

    return max(
        400,
        base_delay - reduction,
    )


# ============================================================
# RESPONSE GENERATION
# ============================================================

def build_response_text(
    analysis: dict[str, Any],
    strategy: str,
) -> str:
    """
    Generate a contextual response from the existing analysis.

    This is intentionally deterministic for now.

    Step 4 will replace this layer with dynamic AI-generated
    dialogue while keeping the same structured response format.
    """

    intent = str(
        analysis.get("intent", "statement")
    ).lower()

    emotion = str(
        analysis.get("emotion", "neutral")
    ).lower()

    topic = str(
        analysis.get("topic", "general")
    ).lower()

    challenge = clamp(
        float(
            analysis.get(
                "challenge_level",
                0.0,
            )
        )
    )

    hostility = clamp(
        float(
            analysis.get(
                "hostility_level",
                0.0,
            )
        )
    )

    # --------------------------------------------------------
    # Greetings
    # --------------------------------------------------------

    if intent == "greeting":
        return (
            "Oh, hello. You finally showed up. "
            "What are we arguing about?"
        )

    # --------------------------------------------------------
    # Questions
    # --------------------------------------------------------

    if intent in {
        "question",
        "asking",
        "inquiry",
    }:
        if topic != "general":
            return (
                f"Alright, let's talk about {topic}. "
                "What's your actual point?"
            )

        return (
            "That's a question. Give me the full argument "
            "and I'll challenge it."
        )

    # --------------------------------------------------------
    # Challenges
    # --------------------------------------------------------

    if (
        strategy == "challenge"
        or challenge >= 0.6
    ):
        if topic != "general":
            return (
                f"You want to challenge me on {topic}? "
                "Alright. Bring your evidence."
            )

        return (
            "That's a bold claim. Go on then. "
            "Defend it."
        )

    # --------------------------------------------------------
    # Hostile input
    # --------------------------------------------------------

    if hostility >= 0.6:
        return (
            "Oh, we're getting serious now? "
            "Fine. Let's actually debate."
        )

    # --------------------------------------------------------
    # Agreement / disagreement
    # --------------------------------------------------------

    if intent in {
        "disagreement",
        "argument",
        "challenge",
    }:
        return (
            "I disagree. And yes, I have a reason. "
            "Let's break this down."
        )

    # --------------------------------------------------------
    # Commands / requests
    # --------------------------------------------------------

    if intent in {
        "request",
        "command",
    }:
        return (
            "Alright. I'll bite. "
            "But don't expect me to make this easy for you."
        )

    # --------------------------------------------------------
    # Topic-specific fallback
    # --------------------------------------------------------

    if topic != "general":
        return (
            f"Interesting argument about {topic}. "
            "Let's see if it actually holds up."
        )

    # --------------------------------------------------------
    # Emotion-specific fallback
    # --------------------------------------------------------

    if emotion in {
        "angry",
        "frustrated",
        "hostile",
    }:
        return (
            "I can tell you're getting fired up. "
            "Good. Now give me your strongest argument."
        )

    if emotion in {
        "happy",
        "excited",
        "playful",
    }:
        return (
            "You're feeling confident, aren't you? "
            "Alright, impress me."
        )

    # --------------------------------------------------------
    # Generic statement
    # --------------------------------------------------------

    return DEFAULT_RESPONSE


# ============================================================
# FACE
# ============================================================

def determine_face(
    strategy: str,
    intensity: float,
    analysis: dict[str, Any],
    personality: dict[str, Any],
) -> str:
    """Determine RageBater's facial expression."""

    intent = str(
        analysis.get(
            "intent",
            "statement",
        )
    ).lower()

    hostility = clamp(
        float(
            analysis.get(
                "hostility_level",
                0.0,
            )
        )
    )

    challenge = clamp(
        float(
            analysis.get(
                "challenge_level",
                0.0,
            )
        )
    )

    playfulness = clamp(
        float(
            personality.get(
                "playfulness",
                0.0,
            )
        )
    )

    # Greetings are intentionally playful.
    if intent == "greeting":
        return "smirk"

    # Hostility takes priority over normal expressions.
    if hostility >= 0.6:
        return "annoyed"

    if strategy == "aggressive_challenge":
        return "annoyed"

    if challenge >= 0.6:
        return "smirk"

    if strategy == "playful_sarcasm":
        return "smirk"

    if playfulness >= 0.65:
        return "smirk"

    if intensity >= 0.8:
        return "rage"

    return "neutral"
# ============================================================
# GESTURE
# ============================================================

def determine_gesture(
    strategy: str,
    intensity: float,
    analysis: dict[str, Any],
) -> str:

    intent = str(
        analysis.get(
            "intent",
            "statement",
        )
    ).lower()

    if strategy in {
        "challenge",
        "aggressive_challenge",
    }:
        return "point"

    if intent in {
        "question",
        "asking",
        "inquiry",
    }:
        return "shrug"

    if intensity >= 0.8:
        return "clap"

    if intensity >= 0.55:
        return "point"

    if strategy == "playful_sarcasm":
        return "point"

    return "idle"


# ============================================================
# ANIMATION
# ============================================================

def determine_animation(
    strategy: str,
    intensity: float,
) -> str:

    if strategy == "aggressive_challenge":
        return "shake"

    if strategy == "challenge":
        return "pulse"

    if strategy == "playful_sarcasm":
        return "bounce"

    if intensity >= 0.8:
        return "shake"

    if intensity >= 0.55:
        return "bounce"

    return "none"


# ============================================================
# STICKER
# ============================================================

def determine_sticker(
    strategy: str,
    analysis: dict[str, Any],
    intensity: float,
) -> str | None:

    challenge = clamp(
        float(
            analysis.get(
                "challenge_level",
                0.0,
            )
        )
    )

    hostility = clamp(
        float(
            analysis.get(
                "hostility_level",
                0.0,
            )
        )
    )

    intent = str(
        analysis.get(
            "intent",
            "statement",
        )
    ).lower()

    # Don't show a sticker on every response.
    # Stickers are reserved for stronger reactions.

    if hostility >= 0.6:
        return "nah_bro"

    if challenge >= 0.6:
        return "you_sure"

    if intent in {
        "question",
        "asking",
        "inquiry",
    }:
        return "really"

    if strategy == "playful_sarcasm":
        return "you_sure"

    if intensity >= 0.75:
        return "nah_bro"

    return None


# ============================================================
# MAIN ADAPTER
# ============================================================

def build_character_response(
    pipeline_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Convert ResponsePipeline output into a complete frontend
    character command.

    All original backend fields are preserved.
    """

    if not isinstance(
        pipeline_result,
        dict,
    ):
        raise TypeError(
            "pipeline_result must be a dictionary"
        )

    analysis = pipeline_result.get(
        "analysis",
        {},
    )

    if not isinstance(
        analysis,
        dict,
    ):
        analysis = {}

    personality = pipeline_result.get(
        "personality",
        {},
    )

    if not isinstance(
        personality,
        dict,
    ):
        personality = {}

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

    response_text = build_response_text(
        analysis=analysis,
        strategy=strategy,
    )

    face = determine_face(
        strategy=strategy,
        intensity=intensity,
        analysis=analysis,
        personality=personality,
    )

    gesture = determine_gesture(
        strategy=strategy,
        intensity=intensity,
        analysis=analysis,
    )

    animation = determine_animation(
        strategy=strategy,
        intensity=intensity,
    )

    sticker = determine_sticker(
        strategy=strategy,
        analysis=analysis,
        intensity=intensity,
    )

    delay_ms = calculate_delay(
        intensity=intensity,
        base_delay=DEFAULT_DELAY_MS,
    )

    chaos_level = chaos_from_intensity(
        intensity
    )

    result = dict(pipeline_result)

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
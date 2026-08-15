from backend.services.response_adapter import (
    build_character_response,
)


def make_pipeline_result(
    *,
    intent="statement",
    topic="general",
    emotion="neutral",
    challenge_level=0.15,
    hostility_level=0.0,
    strategy="neutral_response",
    intensity=0.4,
):
    return {
        "analysis": {
            "intent": intent,
            "topic": topic,
            "emotion": emotion,
            "challenge_level": challenge_level,
            "hostility_level": hostility_level,
            "confidence": 0.7,
        },
        "base_intensity": intensity,
        "intensity": intensity,
        "personality": {
            "aggression": 0.35,
            "confidence": 0.6,
            "irritation": 0.2,
            "playfulness": 0.55,
        },
        "reason": "test",
        "strategy": strategy,
    }


def test_greeting_is_not_generic():
    result = build_character_response(
        make_pipeline_result(
            intent="greeting",
        )
    )

    assert result["response"] != (
        "Interesting. That's a claim. "
        "Now give me something worth arguing about."
    )

    assert result["face"] == "smirk"


def test_python_topic_produces_contextual_response():
    result = build_character_response(
        make_pipeline_result(
            topic="python",
        )
    )

    assert "python" in result["response"].lower()


def test_question_gets_question_behavior():
    result = build_character_response(
        make_pipeline_result(
            intent="question",
        )
    )

    assert result["gesture"] == "shrug"
    assert result["sticker"] == "really"


def test_hostility_changes_character_behavior():
    result = build_character_response(
        make_pipeline_result(
            hostility_level=0.8,
            intensity=0.8,
        )
    )

    assert result["face"] == "annoyed"
    assert result["sticker"] == "nah_bro"


def test_original_pipeline_data_is_preserved():
    result = build_character_response(
        make_pipeline_result(
            topic="python",
        )
    )

    assert result["analysis"]["topic"] == "python"
    assert result["strategy"] == "neutral_response"
    assert "response" in result
    assert "chaos_level" in result
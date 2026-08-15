"""
RageBater Chat API Routes
=========================

Https routes for the ragebatter conversation system
"""

from flask import Blueprint, jsonify, request

from backend.services.response_pipeline import ResponsePipeline
from backend.services.response_adapter import build_character_response


# ============================================================
# BLUEPRINT
# ============================================================

chat_bp = Blueprint("chat", __name__)


# ============================================================
# PIPELINE
# ============================================================

# Keep one pipeline instance alive for the duration of the
# Flask application so personality state persists between
# requests.

response_pipeline = ResponsePipeline()


# ============================================================
# POST /api/chat
# ============================================================

@chat_bp.route("/chat", methods=["POST"])
def chat():
    """
    Process a user chat message.

    Request:

        {
            "message": "hello"
        }

    Response:

        {
            "success": true,
            "data": {
                "analysis": {...},
                "strategy": "...",
                "reason": "...",
                "base_intensity": 0.53,
                "personality": {...},
                "intensity": 0.60,
                "response": "...",
                "face": "...",
                "gesture": "...",
                "animation": "...",
                "sticker": "...",
                "delay_ms": 600,
                "chaos_level": 60
            }
        }
    """

    # --------------------------------------------------------
    # Validate JSON
    # --------------------------------------------------------

    if not request.is_json:
        return jsonify(
            {
                "error": "Request body must contain JSON"
            }
        ), 400

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(
            {
                "error": "Request body must contain JSON"
            }
        ), 400

    # --------------------------------------------------------
    # Validate message
    # --------------------------------------------------------

    message = data.get("message")

    if message is None:
        return jsonify(
            {
                "error": "Message is required"
            }
        ), 400

    if not isinstance(message, str):
        return jsonify(
            {
                "error": "Message must be a string"
            }
        ), 400

    message = message.strip()

    if not message:
        return jsonify(
            {
                "error": "Message cannot be empty"
            }
        ), 400

    # --------------------------------------------------------
    # Run RageBater pipeline
    # --------------------------------------------------------

    pipeline_result = response_pipeline.process(
        message
    )

    # --------------------------------------------------------
    # Convert decision into character command
    # --------------------------------------------------------

    character_response = build_character_response(
        pipeline_result
    )

    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return jsonify(
        {
            "success": True,
            "data": character_response,
        }
    ), 200


# ============================================================
# GET /api/chat/debug
# ============================================================

@chat_bp.route("/chat/debug", methods=["GET"])
def chat_debug():
    """
    Debug endpoint used to verify the complete chat pipeline.
    """

    pipeline_result = response_pipeline.process(
        "hello"
    )

    character_response = build_character_response(
        pipeline_result
    )

    return jsonify(
        {
            "success": True,
            "data": character_response,
        }
    ), 200


# ============================================================
# POST /api/chat/reset
# ============================================================

@chat_bp.route("/chat/reset", methods=["POST"])
def reset_personality():
    """
    Reset the RageBater personality state.
    """

    global response_pipeline

    response_pipeline = ResponsePipeline()

    return jsonify(
        {
            "success": True,
            "message": "Personality reset successfully",
        }
    ), 200
"""
RageBater Chat API Routes
=========================

HTTP routes for the RageBater conversation system.

The route layer is intentionally thin:
    1. Validate HTTP input.
    2. Pass the message to ResponsePipeline.
    3. Return the pipeline result as JSON.
    4. Provide a personality reset endpoint.

The ResponsePipeline remains responsible for:
    - input analysis
    - personality state
    - Rage Engine strategy selection
    - intensity calculation
"""

from flask import Blueprint, jsonify, request

from backend.services.response_pipeline import ResponsePipeline


# ============================================================
# BLUEPRINT
# ============================================================

chat_bp = Blueprint("chat", __name__)


# ============================================================
# PIPELINE
# ============================================================

# Keep one pipeline instance alive for the duration of the
# Flask application so personality state can persist between
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
                "intensity": 0.60
            }
        }
    """

    # --------------------------------------------------------
    # Validate JSON
    # --------------------------------------------------------

    if not request.is_json:
        return jsonify({
            "error": "Request body must contain JSON"
        }), 400

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must contain JSON"
        }), 400

    # --------------------------------------------------------
    # Validate message
    # --------------------------------------------------------

    message = data.get("message")

    if message is None:
        return jsonify({
            "error": "Message is required"
        }), 400

    if not isinstance(message, str):
        return jsonify({
            "error": "Message must be a string"
        }), 400

    message = message.strip()

    if not message:
        return jsonify({
            "error": "Message cannot be empty"
        }), 400

    # --------------------------------------------------------
    # Run RageBater pipeline
    # --------------------------------------------------------

    pipeline_result = response_pipeline.process(message)

    # --------------------------------------------------------
    # Return pipeline result
    # --------------------------------------------------------

    return jsonify({
        "success": True,
        "data": pipeline_result
    }), 200


# ============================================================
# GET /api/chat/debug
# ============================================================

@chat_bp.route("/chat/debug", methods=["GET"])
def chat_debug():
    """
    Debug endpoint used to verify that the chat pipeline is
    working without requiring a request body.
    """

    pipeline_result = response_pipeline.process("hello")

    return jsonify({
        "success": True,
        "data": pipeline_result
    }), 200


# ============================================================
# POST /api/chat/reset
# ============================================================

@chat_bp.route("/chat/reset", methods=["POST"])
def reset_personality():
    """
    Reset the RageBater personality state.

    This endpoint intentionally resets only the current
    ResponsePipeline instance. It does not affect any
    permanent storage because long-term memory is not yet
    implemented.
    """

    # ResponsePipeline currently does not expose a reset()
    # method, so recreate the pipeline instance.
    #
    # Because this route runs against the module-level
    # pipeline, the global reference must be replaced.
    global response_pipeline

    response_pipeline = ResponsePipeline()

    return jsonify({
        "success": True,
        "message": "Personality reset successfully"
    }), 200
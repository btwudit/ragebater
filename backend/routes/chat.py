"""
RageBater Chat API Route

This module handles incoming chat messages and returns
a structured response that the frontend can use to
control the RageBater character.

Current version:
- No Gemini/OpenAI
- No database
- No Rage Engine
- Uses simple mock responses
- Designed for easy debugging
"""

from flask import Blueprint, jsonify, request


# ---------------------------------------------------------
# 1. Blueprint
# ---------------------------------------------------------

chat_bp = Blueprint("chat", __name__)


# ---------------------------------------------------------
# 2. Mock Response Generator
# ---------------------------------------------------------

def generate_mock_response(message):
    """
    Generate a temporary RageBater response.

    This is only for testing the API.
    Later this function will be replaced by the
    Chat Service + Rage Engine + AI Service.
    """

    # Convert message to lowercase so our checks are
    # case-insensitive.
    text = message.lower().strip()

    # ---------------------------------------------
    # Hello
    # ---------------------------------------------

    if "hello" in text or "hi" in text or "hey" in text:
        return {
            "response": "Oh look who decided to show up.",
            "face": "smirk",
            "gesture": "wave",
            "sticker": "really",
            "animation": "bounce",
            "delay_ms": 700,
            "chaos_level": 60,
            "memory_used": False
        }

    # ---------------------------------------------
    # Don't laugh
    # ---------------------------------------------

    if "don't laugh" in text or "do not laugh" in text:
        return {
            "response": "I wasn't laughing. You imagined that.",
            "face": "laugh",
            "gesture": "clap",
            "sticker": "bro_what",
            "animation": "bounce",
            "delay_ms": 900,
            "chaos_level": 82,
            "memory_used": False
        }

    # ---------------------------------------------
    # Python
    # ---------------------------------------------

    if "python" in text:
        return {
            "response": "Python? Okay, I see you came prepared.",
            "face": "smirk",
            "gesture": "shrug",
            "sticker": "really",
            "animation": "bounce",
            "delay_ms": 800,
            "chaos_level": 70,
            "memory_used": False
        }

    # ---------------------------------------------
    # JavaScript
    # ---------------------------------------------

    if "javascript" in text or "javascript" in text:
        return {
            "response": "JavaScript entered the chat. Things are about to get interesting.",
            "face": "confused",
            "gesture": "shrug",
            "sticker": "bro_what",
            "animation": "bounce",
            "delay_ms": 800,
            "chaos_level": 72,
            "memory_used": False
        }

    # ---------------------------------------------
    # Generic response
    # ---------------------------------------------

    return {
        "response": "Interesting. Keep talking, I'm judging respectfully.",
        "face": "smirk",
        "gesture": "shrug",
        "sticker": "really",
        "animation": "bounce",
        "delay_ms": 700,
        "chaos_level": 65,
        "memory_used": False
    }


# ---------------------------------------------------------
# 3. Chat Endpoint
# ---------------------------------------------------------

@chat_bp.route("/chat", methods=["POST"])
def chat():
    """
    Receive a user message and return a RageBater response.

    Final API endpoint:

        POST /api/chat

    The /api prefix is added by app.py when the Blueprint
    is registered.
    """

    # ---------------------------------------------
    # Get JSON body
    # ---------------------------------------------

    data = request.get_json(silent=True)

    # No JSON body
    if data is None:
        return jsonify({
            "error": "Request body must contain JSON"
        }), 400

    # ---------------------------------------------
    # Check message
    # ---------------------------------------------

    if "message" not in data:
        return jsonify({
            "error": "Message is required"
        }), 400

    message = data["message"]

    # ---------------------------------------------
    # Validate message type
    # ---------------------------------------------

    if not isinstance(message, str):
        return jsonify({
            "error": "Message must be a string"
        }), 400

    # ---------------------------------------------
    # Validate empty message
    # ---------------------------------------------

    message = message.strip()

    if not message:
        return jsonify({
            "error": "Message cannot be empty"
        }), 400

    # ---------------------------------------------
    # Generate response
    # ---------------------------------------------

    response_data = generate_mock_response(message)

    # ---------------------------------------------
    # Return API response
    # ---------------------------------------------

    return jsonify({
        "success": True,
        "data": response_data
    }), 200


# ---------------------------------------------------------
# 4. Simple Debug Information
# ---------------------------------------------------------

@chat_bp.route("/chat/debug", methods=["GET"])
def chat_debug():
    """
    Simple debug endpoint.

    Used only to confirm that the chat Blueprint
    is correctly registered.

    Expected URL:

        GET /api/chat/debug
    """

    return jsonify({
        "status": "ok",
        "message": "RageBater chat Blueprint is registered correctly",
        "endpoint": "/api/chat"
    }), 200
"""
This is the main entry point for the RageBater backend server.

It sets up the Flask application, enables CORS, registers the
chat Blueprint, and provides the basic health and root endpoints.

All core logic (AI services, Rage engine, and utilities) will live
in separate modules under backend/ as the project grows.
"""

from flask import Flask, jsonify
from flask_cors import CORS

from routes.chat import chat_bp


# ---------------------------------------------------------
# 1. App Initialization
# ---------------------------------------------------------

# Create the Flask application instance.
app = Flask(__name__)

# Enable Cross-Origin Resource Sharing (CORS).
# This allows the frontend to communicate with the Flask API.
CORS(app)


# ---------------------------------------------------------
# 2. Register Blueprints
# ---------------------------------------------------------

# Register the chat Blueprint.
#
# The /api/chat route is defined inside routes/chat.py,
# so we register the Blueprint here without adding another
# URL prefix.
app.register_blueprint(chat_bp, url_prefix="/api")


# ---------------------------------------------------------
# 3. Health Check Endpoint
# ---------------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health_check():
    """
    Simple health check endpoint for monitoring and
    frontend connection testing.
    """
    return jsonify(
        {
            "status": "healthy",
            "service": "RageBater API"
        }
    ), 200


# ---------------------------------------------------------
# 4. Root Endpoint
# ---------------------------------------------------------

@app.route("/", methods=["GET"])
def root():
    """
    Root endpoint to verify that the server is running.
    """
    return jsonify(
        {
            "message": "RageBater API is running",
            "status": "online"
        }
    ), 200


# ---------------------------------------------------------
# 5. Error Handlers
# ---------------------------------------------------------

@app.errorhandler(404)
def not_found(error):
    """
    Handle 404 errors.
    Returns a JSON response instead of Flask's default HTML page.
    """
    return jsonify(
        {
            "error": "Route not found"
        }
    ), 404


@app.errorhandler(500)
def internal_error(error):
    """
    Handle 500 errors.
    Returns a JSON response so the frontend can parse it.
    """
    return jsonify(
        {
            "error": "Internal server error"
        }
    ), 500


# ---------------------------------------------------------
# 6. Application Entry Point
# ---------------------------------------------------------

if __name__ == "__main__":
    # Run the Flask development server.
    #
    # host="0.0.0.0" makes the server accessible through
    # the Codespace forwarded port.
    #
    # port=5000 is the RageBater backend port.
    #
    # debug=True enables automatic reloading during development.
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
"""
RageBater Flask API + Frontend Entry Point
===========================================

Main entry point for the RageBater application.

The Flask application serves:

Frontend:
    GET  /
    GET  /css/<path>
    GET  /js/<path>

Backend API:
    GET  /api/health
    POST /api/chat
    GET  /api/chat/debug
    POST /api/chat/reset

Run from the project root with:

    python -m backend.app
"""

from __future__ import annotations

import os
import sys

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS


# ============================================================
# 1. PATH CONFIGURATION
# ============================================================

# backend/app.py:
#
#     project/
#     ├── backend/
#     │   └── app.py
#     └── frontend/
#         ├── index.html
#         ├── css/
#         └── js/
#
# Therefore the project root is one directory above backend/.

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")


# ============================================================
# 2. PACKAGE PATH COMPATIBILITY
# ============================================================

# Some existing engine/service modules use imports such as:
#
#     from engine.intensity_controller import ...
#
# rather than:
#
#     from backend.engine.intensity_controller import ...
#
# Keep the existing architecture working without rewriting
# those modules.

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


# ============================================================
# 3. IMPORT ROUTES
# ============================================================

from backend.routes.chat import chat_bp


# ============================================================
# 4. FLASK APPLICATION
# ============================================================

app = Flask(__name__)


# ============================================================
# 5. CORS
# ============================================================

# Keep CORS enabled because the frontend may still be accessed
# from a different origin during development.

CORS(app)


# ============================================================
# 6. REGISTER API BLUEPRINTS
# ============================================================

# chat.py defines:
#
#     /chat
#     /chat/debug
#     /chat/reset
#
# Registering with /api produces:
#
#     POST /api/chat
#     GET  /api/chat/debug
#     POST /api/chat/reset

app.register_blueprint(
    chat_bp,
    url_prefix="/api",
)


# ============================================================
# 7. FRONTEND
# ============================================================

@app.route("/", methods=["GET"])
def serve_frontend():
    """
    Serve the main RageBater frontend.

    The frontend entry point is:

        frontend/index.html
    """

    return send_from_directory(
        FRONTEND_DIR,
        "index.html",
    )


@app.route("/<path:path>", methods=["GET"])
def serve_frontend_assets(path: str):
    """
    Serve frontend static assets.

    Examples:

        /css/style.css
        /js/app.js

    API routes are registered separately under /api and therefore
    continue to use the API blueprint.
    """

    requested_path = os.path.join(FRONTEND_DIR, path)

    # Only serve files that actually exist.
    if os.path.isfile(requested_path):
        return send_from_directory(
            FRONTEND_DIR,
            path,
        )

    return jsonify(
        {
            "error": "Route not found",
        }
    ), 404


# ============================================================
# 8. ROOT API INFORMATION
# ============================================================

# NOTE:
# The root URL now serves the frontend.
#
# The API health endpoint remains the canonical backend
# availability check.


# ============================================================
# 9. HEALTH CHECK
# ============================================================

@app.route("/api/health", methods=["GET"])
def health_check():
    """
    Health endpoint used to verify that the backend is running.
    """

    return jsonify(
        {
            "status": "healthy",
            "service": "RageBater API",
        }
    ), 200


# ============================================================
# 10. 404 HANDLER
# ============================================================

@app.errorhandler(404)
def not_found(error):
    """
    Return JSON for unknown routes instead of Flask's default
    HTML 404 response.
    """

    return jsonify(
        {
            "error": "Route not found",
        }
    ), 404


# ============================================================
# 11. 500 HANDLER
# ============================================================

@app.errorhandler(500)
def internal_error(error):
    """
    Return JSON instead of Flask's default HTML 500 page.
    """

    return jsonify(
        {
            "error": "Internal server error",
        }
    ), 500


# ============================================================
# 12. APPLICATION STARTUP
# ============================================================

if __name__ == "__main__":
    """
    Start the RageBater development server.

    host=0.0.0.0
        Required for GitHub Codespaces port forwarding.

    port=5000
        RageBater development server port.

    debug=True
        Enables Flask development debugging and reload.
    """

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )
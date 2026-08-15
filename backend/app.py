"""
RageBater Flask API Entry Point
================================

Main entry point for the RageBater backend.

Project structure:

    backend/
    ├── app.py
    ├── engine/
    ├── routes/
    ├── services/
    └── utils/

Run from the project root with:

    python -m backend.app

The application exposes:

    GET  /
    GET  /api/health
    POST /api/chat
    GET  /api/chat/debug

The frontend communicates with:

    /api/chat
"""

from __future__ import annotations

import os
import sys

from flask import Flask, jsonify
from flask_cors import CORS


# ============================================================
# 1. PACKAGE PATH COMPATIBILITY
# ============================================================
#
# RageBater is now executed as:
#
#     python -m backend.app
#
# Therefore Python correctly recognizes "backend" as a package.
#
# Some of the existing engine/service files were written with
# imports such as:
#
#     from engine.intensity_controller import ...
#
# instead of:
#
#     from backend.engine.intensity_controller import ...
#
# Adding the backend directory to sys.path here keeps those
# existing modules working without changing the architecture
# of the project in this step.
#
# This is intentionally done BEFORE importing chat_bp.

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


# ============================================================
# 2. IMPORT ROUTES
# ============================================================
#
# IMPORTANT:
# Use the package-qualified import because this application
# is launched with:
#
#     python -m backend.app
#

from backend.routes.chat import chat_bp


# ============================================================
# 3. FLASK APPLICATION
# ============================================================

app = Flask(__name__)


# ============================================================
# 4. CORS
# ============================================================
#
# The frontend and backend may be served from different
# origins during Codespaces/development.
#
# CORS allows the browser frontend to communicate with Flask.

CORS(app)


# ============================================================
# 5. REGISTER BLUEPRINTS
# ============================================================
#
# chat.py contains:
#
#     @chat_bp.route("/chat")
#
# Registering it with:
#
#     url_prefix="/api"
#
# produces:
#
#     POST /api/chat
#     GET  /api/chat/debug
#

app.register_blueprint(
    chat_bp,
    url_prefix="/api",
)


# ============================================================
# 6. ROOT ENDPOINT
# ============================================================

@app.route("/", methods=["GET"])
def root():
    """
    Basic endpoint used to verify that the RageBater
    Flask server is running.
    """

    return jsonify(
        {
            "message": "RageBater API is running",
            "status": "online",
        }
    ), 200


# ============================================================
# 7. HEALTH CHECK
# ============================================================

@app.route("/api/health", methods=["GET"])
def health_check():
    """
    Health endpoint for backend/frontend connection testing.
    """

    return jsonify(
        {
            "status": "healthy",
            "service": "RageBater API",
        }
    ), 200


# ============================================================
# 8. 404 HANDLER
# ============================================================

@app.errorhandler(404)
def not_found(error):
    """
    Return JSON instead of Flask's default HTML 404 page.
    """

    return jsonify(
        {
            "error": "Route not found",
        }
    ), 404


# ============================================================
# 9. 500 HANDLER
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
# 10. APPLICATION STARTUP
# ============================================================

if __name__ == "__main__":
    """
    Start the RageBater development server.

    host=0.0.0.0
        Required so the application is reachable through
        GitHub Codespaces port forwarding.

    port=5000
        RageBater backend port.

    debug=True
        Enables Flask development debugging and reload.
    """

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )
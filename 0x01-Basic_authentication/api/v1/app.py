#!/usr/bin/env python3
"""
API module with routes and error handlers
"""

from os import getenv
from api.v1.views import app_views
from flask import Flask, jsonify, abort, request
from flask_cors import CORS


app = Flask(__name__)
app.register_blueprint(app_views)

# Enable CORS for the entire app
CORS(app, resources={r"/api/v1/*": {"origins": "*"}})

# Determine the authentication type to use
auth_type = getenv("AUTH_TYPE")
if auth_type == "auth":
    from api.v1.auth.auth import Auth
    auth = Auth()
elif auth_type == "basic_auth":
    from api.v1.auth.basic_auth import BasicAuth
    auth = BasicAuth()
else:
    auth = None


@app.errorhandler(404)
def not_found(error) -> str:
    """
    Error handler for 404 Not Found
    """
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(401)
def unauthorized_error(error) -> str:
    """
    Error handler for 401 Unauthorized
    """
    return jsonify({"error": "Unauthorized"}), 401


@app.errorhandler(403)
def forbidden_error(error) -> str:
    """
    Error handler for 403 Forbidden
    """
    return jsonify({"error": "Forbidden"}), 403


@app.before_request
def before_request() -> str:
    """
    Filter for incoming requests
    """
    request_path_list = [
        '/api/v1/status/',
        '/api/v1/unauthorized/',
        '/api/v1/forbidden/'
    ]
    if auth:
        if auth.require_auth(request.path, request_path_list):
            if auth.authorization_header(request) is None:
                abort(401)
            if auth.current_user(request) is None:
                abort(403)


if __name__ == "__main__":
    host = getenv("API_HOST", "0.0.0.0")
    port = getenv("API_PORT", "5000")
    app.run(host=host, port=port)

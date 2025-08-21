# utils/auth.py
from flask import request, jsonify, current_app

def api_key_auth():
    """Middleware to check for API Key for protected methods."""
    # Methods that require API key authentication
    protected_methods = ['POST', 'PATCH', 'DELETE']

    if request.method in protected_methods:
        # Get API key from request headers. Using 'Api-Key' as per new standard.
        api_key = request.headers.get('Api-Key')
        
        # Get the expected API key from configuration
        expected_api_key = current_app.config.get('API_KEY')

        # Validate API key
        if not api_key or api_key != expected_api_key:
            current_app.logger.warning(
                f"Unauthorized access attempt from {request.remote_addr} with method {request.method}. Missing or invalid 'Api-Key' header."
            )
            return jsonify({"error": "Unauthorized: Invalid or missing API Key"}), 401

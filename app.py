# app.py
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from pydantic import ValidationError

from config import Config
from logging_config import setup_logging # Import the setup function
from utils.auth import api_key_auth # NEW: Import api_key_auth

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    """
    Application Factory: Creates and configures the Flask application.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # --- Setup Logging ---
    # This should be one of the first things to configure
    setup_logging(app)

    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)

    # --- Register Request Handler ---
    @app.before_request
    def log_request_info():
        """Log information about each incoming request."""
        app.logger.info(
            'Request: %s %s from %s',
            request.method,
            request.path,
            request.remote_addr
        )

    # Import and register blueprints
    from routes.books import books_bp
    from routes.categories import categories_bp
    from routes.borrowings import borrowings_bp
    
    # Register blueprints with standardized URL prefixes (no trailing slashes)
    app.register_blueprint(books_bp, url_prefix='/api/books')
    app.register_blueprint(categories_bp, url_prefix='/api/categories')
    app.register_blueprint(borrowings_bp, url_prefix='/api/borrowings')

    # --- API Key Authentication ---
    # Register the API key authentication function from utils/auth.py
    app.before_request(api_key_auth)
        
    # --- Global Error Handlers ---
    @app.errorhandler(ValidationError)
    def handle_pydantic_validation_error(error):
        """Catch Pydantic validation errors and return a standardized JSON response."""
        app.logger.warning(
            f"Validation error: {error.errors()} from {request.remote_addr}"
        )
        response = {
            "error": "Validation failed",
            "details": error.errors()
        }
        return jsonify(response), 400

    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 Not Found errors."""
        app.logger.info(
            f"404 Not Found: {request.path} from {request.remote_addr}"
        )
        return jsonify({"error": "The requested resource was not found."}), 404
        
    @app.errorhandler(Exception)
    def handle_generic_error(error):
        """
        Handle all other exceptions, including 500 Internal Server Error.
        This is a catch-all handler.
        """
        # Log the full exception traceback for debugging
        app.logger.error(
            f"Unhandled exception: {error}", exc_info=True
        )
        if db.session.is_active:
            db.session.rollback()
        return jsonify({"error": "An unexpected internal error occurred."}), 500

    return app

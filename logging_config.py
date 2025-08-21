# logging_config.py
import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging(app):
    """
    Configures application-wide logging based on Flask config.

    Supports logging to a rotating file and/or standard output (stdout).
    """
    # Remove default handlers to avoid duplicate logs
    if app.logger.hasHandlers():
        app.logger.handlers.clear()

    # Get log configuration from app.config, with defaults
    log_file = app.config.get('LOG_FILE')
    log_level_str = app.config.get('LOG_LEVEL', 'INFO').upper()
    log_to_stdout = app.config.get('LOG_TO_STDOUT', True) # Default to True for development

    # Convert string log level to logging constant
    log_level = getattr(logging, log_level_str, logging.INFO)

    # Define a standard formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    )

    # --- File Handler ---
    # Create a rotating file handler if a LOG_FILE is specified in the config
    if log_file:
        try:
            # Ensure the directory for the log file exists
            log_dir = os.path.dirname(log_file)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # Create the file handler
            # Rotates when the log file reaches 1MB, keeps 5 backup logs
            file_handler = RotatingFileHandler(
                log_file, 
                maxBytes=1024 * 1024, # 1 MB
                backupCount=5
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(log_level)
            app.logger.addHandler(file_handler)
            app.logger.info(f"Logging configured to file: {log_file}")

        except (OSError, IOError) as e:
            # Handle potential file system errors gracefully
            app.logger.error(f"Error setting up file logger at {log_file}: {e}", exc_info=True)


    # --- Console/Stream Handler ---
    # Add a stream handler to output logs to the console if enabled
    # This is useful for development and environments like Docker or cPanel's log stream
    if log_to_stdout:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(log_level)
        app.logger.addHandler(stream_handler)
        app.logger.info("Logging configured to stream (stdout).")

    # Set the overall logger level for the app
    app.logger.setLevel(log_level)

    # Log application startup
    app.logger.info("Flask application starting up...")

# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    
    # --- Database Configuration ---
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_HOST = os.environ.get('DB_HOST')
    DB_PORT = os.environ.get('DB_PORT', 5432)
    DB_NAME = os.environ.get('DB_NAME')

    if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_NAME]):
        raise ValueError("Database credentials are not fully set in .env file.")

    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # --- Logging Configuration ---
    # Log level can be DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
    
    # Path to the log file. If not set, logs will not be written to a file.
    # For cPanel, this could be something like '/home/your_cpanel_user/logs/app.log'
    LOG_FILE = os.environ.get('LOG_FILE') # e.g., 'logs/app.log'

    # Set to False in production if you only want to log to the file
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT', 'True').lower() in ['true', '1', 't']

    # --- API Key for restricted endpoints ---
    API_KEY = os.environ.get('API_KEY')

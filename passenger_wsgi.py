# passenger_wsgi.py
import os
import sys

# Add the project directory to the Python path to allow imports
sys.path.insert(0, os.path.dirname(__file__))

# Import the application factory and create the application instance
from app import create_app

# The 'application' variable is what Passenger looks for
application = create_app()

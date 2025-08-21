#!/bin/sh
# devserver.sh

# Activate the Python virtual environment
source .venv/bin/activate

# Set the FLASK_APP environment variable so 'flask' commands work
export FLASK_APP=app.py

# Run the Python development server
# The script will now use the python from the activated venv
echo "Starting Flask development server on http://localhost:5001..."
python dev_server.py

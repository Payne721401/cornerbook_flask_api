#!/bin/bash
# init_db.sh
# This script completely resets and initializes the local PostgreSQL database.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
# Activate Python virtual environment to access flask and other packages
echo ">>> Activating Python virtual environment..."
source .venv/bin/activate

# Load database credentials from .env file
echo ">>> Loading database credentials from .env file..."
set -a
source .env
set +a

# Define PostgreSQL data directory and log file
PG_DATA="/tmp/postgres"
LOGFILE="$PG_DATA/logfile"

# --- Main Execution ---

# 1. Stop any existing PostgreSQL server and clean up old data
echo ">>> Stopping any running PostgreSQL server and cleaning up old data..."
pg_ctl stop -D "$PG_DATA" -m fast || true
rm -rf "$PG_DATA"

# 2. Initialize a new PostgreSQL database cluster
echo ">>> Initializing new PostgreSQL data directory at $PG_DATA..."
initdb -D "$PG_DATA" --auth-local=trust

# 3. Start the new PostgreSQL server
echo ">>> Starting PostgreSQL server..."
pg_ctl start -D "$PG_DATA" -l "$LOGFILE" -o "-k /tmp"
sleep 2

# 4. Create users and databases via psql script
echo ">>> Creating user and databases ($DB_NAME and ${DB_NAME}_test)..."
psql -h /tmp -U user -d postgres <<-EOSQL
    \set ON_ERROR_STOP on
    CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';
    CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};
    CREATE DATABASE ${DB_NAME}_test OWNER ${DB_USER};
EOSQL

# 5. Grant permissions to the new databases
echo ">>> Granting privileges..."
psql -h /tmp -U user -d "${DB_NAME}" <<-EOSQL
    \set ON_ERROR_STOP on
    GRANT ALL ON SCHEMA public TO ${DB_USER};
    GRANT CREATE ON SCHEMA public TO ${DB_USER};
EOSQL
psql -h /tmp -U user -d "${DB_NAME}_test" <<-EOSQL
    \set ON_ERROR_STOP on
    GRANT ALL ON SCHEMA public TO ${DB_USER};
    GRANT CREATE ON SCHEMA public TO ${DB_USER};
EOSQL

# 6. Run Flask database migrations on the development database
echo ">>> Running database migrations on development database..."
export FLASK_APP=app.py
# Add current directory to PYTHONPATH to ensure modules are found
export PYTHONPATH=.
flask db upgrade

echo ""
echo "✅ Database initialization complete!"
echo "   - PostgreSQL server is running."
echo "   - User '${DB_USER}' created."
echo "   - Databases '${DB_NAME}' and '${DB_NAME}_test' created and configured."
echo "   - Application tables created in '${DB_NAME}'."
echo "You can now start the Flask server by running: python dev_server.py"

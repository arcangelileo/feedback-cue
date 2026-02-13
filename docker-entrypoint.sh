#!/bin/bash
set -e

echo "FeedbackCue starting..."

# Run database migrations
cd /app
echo "Running database migrations..."
python -m alembic upgrade head || {
    echo "ERROR: Database migration failed! Check your DATABASE_URL and migration files."
    exit 1
}
echo "Migrations complete."

# Start the application (exec replaces the shell for proper signal handling)
exec "$@"

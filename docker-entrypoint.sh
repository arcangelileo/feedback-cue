#!/bin/bash
set -e

# Run database migrations
cd /app
python -m alembic upgrade head 2>/dev/null || echo "No migrations to run (tables created on startup)"

# Start the application
exec "$@"

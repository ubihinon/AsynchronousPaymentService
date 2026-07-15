#!/bin/bash
set -e

# --- ADD THIS DEBUG SECTION ---
echo "Checking PyCharm Helpers..."
if [ -d "/opt/.pycharm_helpers" ]; then
  echo "✅ Helpers directory found"
  ls -l /opt/.pycharm_helpers/pydev/pydevd.py || echo "❌ pydevd.py NOT found in directory"
else
  echo "❌ /opt/.pycharm_helpers directory is MISSING"
fi
# ------------------------------

echo "Waiting for database..."
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 1
done
echo "Database is ready!"

echo "Running migrations..."
alembic upgrade head

echo "Starting application..."
exec "$@"

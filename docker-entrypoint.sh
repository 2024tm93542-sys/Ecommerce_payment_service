#!/bin/sh

# Exit on error
set -e

# Wait for MySQL to be ready
echo "Waiting for MySQL..."
while ! nc -z db 3306; do
  sleep 1
done
echo "MySQL is ready!"

# Execute the command passed to docker (usually uvicorn)
exec "$@"
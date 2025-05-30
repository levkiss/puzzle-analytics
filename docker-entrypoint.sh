#!/bin/bash
set -e

echo "Starting Puzzle Swap ETL..."

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
while ! pg_isready -h postgres -p 5432 -U puzzle_user; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 2
done

echo "PostgreSQL is ready!"

# Initialize database schema
echo "Initializing database schema..."
poetry run puzzle-etl init-db

# Run the ETL pipeline
echo "Starting ETL pipeline..."
exec "$@" 
#!/bin/bash

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
while ! pg_isready -h postgres -p 5432 -U puzzle_user; do
  echo "PostgreSQL is not ready yet. Waiting..."
  sleep 2
done

echo "PostgreSQL is ready!"

# Initialize Superset database
echo "Initializing Superset database..."
superset db upgrade

# Create admin user if it doesn't exist
echo "Creating admin user..."
superset fab create-admin \
    --username admin \
    --firstname Admin \
    --lastname User \
    --email admin@puzzle-swap.com \
    --password admin || echo "Admin user already exists"

# Initialize Superset
echo "Initializing Superset..."
superset init

# Load example data (optional)
echo "Loading examples..."
superset load_examples || echo "Examples already loaded or failed to load"

echo "Superset initialization completed!" 
 
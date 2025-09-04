#!/bin/bash

# Database setup script for Julie Django project
echo "Setting up PostgreSQL database for Julie project..."

# Check if PostgreSQL is running
if ! pg_isready -q; then
    echo "PostgreSQL is not running. Please start PostgreSQL first."
    exit 1
fi

# Create database and user
echo "Creating database and user..."
psql -U postgres -c "CREATE DATABASE julie_db;" 2>/dev/null || echo "Database julie_db already exists or could not be created"
psql -U postgres -c "CREATE USER julie_user WITH PASSWORD 'julie_password';" 2>/dev/null || echo "User julie_user already exists or could not be created"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE julie_db TO julie_user;" 2>/dev/null || echo "Privileges already granted or could not be granted"
psql -U postgres -c "ALTER USER julie_user CREATEDB;" 2>/dev/null || echo "User already has CREATEDB privilege or could not be granted"

echo "Database setup complete!"
echo "You can now run: python manage.py migrate" 
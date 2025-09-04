#!/bin/bash

# Quick Django Migration Script - Non-interactive
echo "🚀 Quick Django migrations for Julie project..."

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: manage.py not found. Please run this script from the project root directory."
    exit 1
fi

# Run makemigrations
echo "📝 Running makemigrations..."
python manage.py makemigrations

if [ $? -eq 0 ]; then
    echo "✅ Makemigrations completed successfully!"
else
    echo "❌ Makemigrations failed!"
    exit 1
fi

# Run migrate
echo "🔄 Running migrate..."
python manage.py migrate

if [ $? -eq 0 ]; then
    echo "✅ Migrate completed successfully!"
    echo ""
    echo "🎉 All migrations completed successfully!"
else
    echo "❌ Migrate failed!"
    exit 1
fi 
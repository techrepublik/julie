#!/bin/bash

# Django Migration Script for Julie project
echo "🚀 Starting Django migrations for Julie project..."

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: manage.py not found. Please run this script from the project root directory."
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: Virtual environment not detected. Make sure you have Django installed."
fi

# Function to run makemigrations
run_makemigrations() {
    echo "📝 Running makemigrations..."
    python manage.py makemigrations
    
    if [ $? -eq 0 ]; then
        echo "✅ Makemigrations completed successfully!"
    else
        echo "❌ Makemigrations failed!"
        return 1
    fi
}

# Function to run migrate
run_migrate() {
    echo "🔄 Running migrate..."
    python manage.py migrate
    
    if [ $? -eq 0 ]; then
        echo "✅ Migrate completed successfully!"
    else
        echo "❌ Migrate failed!"
        return 1
    fi
}

# Function to show migration status
show_status() {
    echo "📊 Migration status:"
    python manage.py showmigrations
}

# Function to show pending migrations
show_pending() {
    echo "⏳ Pending migrations:"
    python manage.py showmigrations --list | grep -E "\[ \]" || echo "No pending migrations found."
}

# Main execution
echo "🔍 Checking current migration status..."
show_status

echo ""
echo "📋 Available options:"
echo "1) Run makemigrations only"
echo "2) Run migrate only"
echo "3) Run both makemigrations and migrate (recommended)"
echo "4) Show migration status"
echo "5) Show pending migrations"
echo "6) Exit"

read -p "Choose an option (1-6): " choice

case $choice in
    1)
        run_makemigrations
        ;;
    2)
        run_migrate
        ;;
    3)
        echo "🔄 Running both makemigrations and migrate..."
        if run_makemigrations; then
            run_migrate
        else
            echo "❌ Stopping due to makemigrations failure."
            exit 1
        fi
        ;;
    4)
        show_status
        ;;
    5)
        show_pending
        ;;
    6)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid option. Please choose 1-6."
        exit 1
        ;;
esac

echo ""
echo "🎉 Migration process completed!"
echo "💡 Tip: You can also run individual commands:"
echo "   python manage.py makemigrations"
echo "   python manage.py migrate"
echo "   python manage.py showmigrations" 
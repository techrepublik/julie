#!/bin/bash

# Log Management Script for Julie Django project
echo "📋 Log Management for Julie Project"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: manage.py not found. Please run this script from the project root directory."
    exit 1
fi

# Function to show log file sizes
show_log_sizes() {
    echo "📊 Current Log File Sizes:"
    echo "-------------------------"
    if [ -d "logs" ]; then
        ls -lh logs/*.log 2>/dev/null | while read line; do
            echo "   $line"
        done
    else
        echo "   No logs directory found"
    fi
}

# Function to view recent logs
view_recent_logs() {
    local log_file=$1
    local lines=${2:-20}
    
    if [ -f "logs/$log_file" ]; then
        echo "📖 Recent $lines lines from $log_file:"
        echo "----------------------------------------"
        tail -n $lines "logs/$log_file"
    else
        echo "❌ Log file logs/$log_file not found"
    fi
}

# Function to clean old log files
clean_old_logs() {
    echo "🧹 Cleaning old log files..."
    if [ -d "logs" ]; then
        # Remove log files older than 30 days
        find logs -name "*.log.*" -mtime +30 -delete 2>/dev/null
        echo "✅ Old log files cleaned"
    else
        echo "❌ No logs directory found"
    fi
}

# Function to monitor logs in real-time
monitor_logs() {
    local log_file=$1
    if [ -f "logs/$log_file" ]; then
        echo "👀 Monitoring logs/$log_file (Press Ctrl+C to stop)..."
        tail -f "logs/$log_file"
    else
        echo "❌ Log file logs/$log_file not found"
    fi
}

# Main menu
while true; do
    echo ""
    echo "📋 Available options:"
    echo "1) Show log file sizes"
    echo "2) View recent app_log.log"
    echo "3) View recent django.log"
    echo "4) View recent error.log"
    echo "5) View recent security.log"
    echo "6) Monitor app_log.log in real-time"
    echo "7) Clean old log files"
    echo "8) Test logging (run test script)"
    echo "9) Exit"
    
    read -p "Choose an option (1-9): " choice
    
    case $choice in
        1)
            show_log_sizes
            ;;
        2)
            view_recent_logs "app_log.log" 20
            ;;
        3)
            view_recent_logs "django.log" 20
            ;;
        4)
            view_recent_logs "error.log" 20
            ;;
        5)
            view_recent_logs "security.log" 20
            ;;
        6)
            monitor_logs "app_log.log"
            ;;
        7)
            clean_old_logs
            ;;
        8)
            echo "🧪 Running logging test..."
            python3 test_logging.py
            ;;
        9)
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            echo "❌ Invalid option. Please choose 1-9."
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
done 
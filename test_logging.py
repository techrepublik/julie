#!/usr/bin/env python3
"""
Test script to demonstrate logging functionality
Run this script to test different log levels and see how they're handled
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'julie.settings')
django.setup()

import logging

# Get loggers for different components
logger = logging.getLogger(__name__)
api_logger = logging.getLogger('api')
accounts_logger = logging.getLogger('accounts')
django_logger = logging.getLogger('django')

def test_logging():
    """Test different logging levels and see how they're handled"""
    
    print("🧪 Testing Django Logging Configuration")
    print("=" * 50)
    
    # Test different log levels
    logger.debug("This is a DEBUG message - should only appear in console")
    logger.info("This is an INFO message - should appear in console and app_log.log")
    logger.warning("This is a WARNING message - should appear in console and app_log.log")
    logger.error("This is an ERROR message - should appear in console, app_log.log, and error.log")
    
    print("\n📝 Testing API Logger")
    api_logger.info("API logger test message")
    api_logger.warning("API warning message")
    
    print("\n👤 Testing Accounts Logger")
    accounts_logger.info("Accounts logger test message")
    accounts_logger.error("Accounts error message")
    
    print("\n🌐 Testing Django Logger")
    django_logger.info("Django framework message")
    
    print("\n✅ Logging test completed!")
    print("\n📁 Check the following log files:")
    print("   - logs/app_log.log (main application logs)")
    print("   - logs/django.log (Django framework logs)")
    print("   - logs/error.log (error logs)")
    print("   - logs/security.log (security logs)")
    
    print("\n💡 Log files will automatically rotate when they reach:")
    print("   - app_log.log: 10MB (keeps 5 backup files)")
    print("   - django.log: 10MB (keeps 5 backup files)")
    print("   - error.log: 10MB (keeps 5 backup files)")
    print("   - security.log: 5MB (keeps 3 backup files)")

if __name__ == '__main__':
    test_logging() 
#!/usr/bin/env python3
"""
WSGI entry point for production deployment.
"""
import os
import sys

# Ensure the app directory is in the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from app import create_app
    
    # Create the Flask app instance
    app = create_app(os.getenv('FLASK_ENV', 'production'))
    
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

if __name__ == "__main__":
    app.run()

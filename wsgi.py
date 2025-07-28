#!/usr/bin/env python3
"""
WSGI entry point for production deployment.
"""
import os
from app import create_app

# Create the Flask app instance
app = create_app(os.getenv('FLASK_ENV', 'production'))

if __name__ == "__main__":
    app.run()

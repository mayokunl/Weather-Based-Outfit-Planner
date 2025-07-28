#!/usr/bin/env python3
"""
Main entry point for the Weather-Based Outfit Planner application.
"""
import os
from app import create_app

# Import legacy database initialization
from db import init_db

def main():
    # Initialize legacy database
    init_db()
    
    # Create Flask app
    config_name = os.getenv('FLASK_ENV', 'development')
    app = create_app(config_name)
    
    # Run the application
    app.run(
        debug=True if config_name == 'development' else False,
        port=int(os.getenv('PORT', 5001))
    )

if __name__ == '__main__':
    main()

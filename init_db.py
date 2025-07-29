#!/usr/bin/env python3
"""
Database initialization script for Weather-Based-Outfit-Planner
This script creates all necessary database tables and handles migrations.
"""

import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.closet import ClosetItem
from app.models.trip import Trip

def init_database():
    """Initialize the database with all tables."""
    app = create_app()
    
    with app.app_context():
        try:
            # Create all tables
            print("Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Verify tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📋 Created tables: {', '.join(tables)}")
            
            # Check if ClosetItem table has the correct columns
            if 'closet_item' in tables:
                columns = [col['name'] for col in inspector.get_columns('closet_item')]
                print(f"🔍 ClosetItem columns: {', '.join(columns)}")
                
                required_columns = ['id', 'user_id', 'title', 'item_type', 'price', 'image_url', 'source']
                missing_columns = [col for col in required_columns if col not in columns]
                
                if missing_columns:
                    print(f"⚠️  Missing columns in ClosetItem: {', '.join(missing_columns)}")
                else:
                    print("✅ ClosetItem table has all required columns!")
            
        except Exception as e:
            print(f"❌ Error creating database: {e}")
            return False
    
    return True

if __name__ == "__main__":
    if init_database():
        print("\n🎉 Database initialization completed successfully!")
        print("You can now run the application with: python app/app.py")
    else:
        print("\n💥 Database initialization failed!")
        sys.exit(1)

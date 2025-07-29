#!/usr/bin/env python3
"""
Script to update dress items in the closet database.
This will move dress items from 'bottoms' category to 'dress' category.
"""

import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.closet import ClosetItem

def update_dress_categories():
    """Update dress items to use the correct 'dress' category."""
    app = create_app()
    
    with app.app_context():
        try:
            # Find all items that contain "dress" in the title but are categorized as "bottoms"
            dress_items = ClosetItem.query.filter(
                ClosetItem.title.ilike('%dress%'),
                ClosetItem.item_type.in_(['bottoms', 'bottom'])
            ).all()
            
            print(f"Found {len(dress_items)} dress items to update...")
            
            for item in dress_items:
                old_category = item.item_type
                item.item_type = 'dress'
                print(f"  • Updated '{item.title}' from '{old_category}' to 'dress'")
            
            # Also check for other dress-related terms
            other_dress_terms = ['gown', 'frock', 'sundress', 'maxi', 'mini dress']
            for term in other_dress_terms:
                items = ClosetItem.query.filter(
                    ClosetItem.title.ilike(f'%{term}%'),
                    ClosetItem.item_type.in_(['bottoms', 'bottom', 'other'])
                ).all()
                
                for item in items:
                    old_category = item.item_type
                    item.item_type = 'dress'
                    print(f"  • Updated '{item.title}' from '{old_category}' to 'dress'")
            
            # Commit all changes
            db.session.commit()
            print(f"✅ Successfully updated dress categories!")
            
            # Show current category distribution
            print("\n📊 Current category distribution:")
            categories = db.session.query(ClosetItem.item_type, db.func.count(ClosetItem.id)).group_by(ClosetItem.item_type).all()
            for category, count in categories:
                print(f"  • {category}: {count} items")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error updating categories: {e}")
            return False
    
    return True

if __name__ == "__main__":
    if update_dress_categories():
        print("\n🎉 Category update completed successfully!")
    else:
        print("\n💥 Category update failed!")
        sys.exit(1)

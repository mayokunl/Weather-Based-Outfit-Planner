# Script to fix plural item_type values in ClosetItem table
from app import create_app, db
from app.models.closet import ClosetItem

# Map plural to singular for known categories
PLURAL_TO_SINGULAR = {
    'dresses': 'dress',
    'tops': 'top',
    'bottoms': 'bottom',
    'shoes': 'shoe',
    'accessories': 'accessory',
    'jewelries': 'jewelry',
    'bags': 'bag',
    'others': 'other',
}

def fix_plural_item_types():
    app = create_app()
    with app.app_context():
        updated = 0
        for plural, singular in PLURAL_TO_SINGULAR.items():
            items = ClosetItem.query.filter_by(item_type=plural).all()
            for item in items:
                item.item_type = singular
                updated += 1
        if updated:
            db.session.commit()
            print(f"Updated {updated} items to use singular item_type.")
        else:
            print("No plural item_type values found.")

if __name__ == "__main__":
    fix_plural_item_types()

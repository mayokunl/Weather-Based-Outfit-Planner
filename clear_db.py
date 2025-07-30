# clear_db.py
"""
Script to delete all users and trips from the database.
WARNING: This is destructive and cannot be undone.
"""
from app import create_app, db
from app.models.user import User
from app.models.trip import Trip

app = create_app()
with app.app_context():
    print("Deleting all trips...")
    Trip.query.delete()
    print("Deleting all users...")
    User.query.delete()
    db.session.commit()
    print("All users and trips deleted.")

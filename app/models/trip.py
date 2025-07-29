from app import db
from app.models.user import User
import json

class Trip(db.Model):
    """Trip model for Flask-SQLAlchemy ORM."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    region = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10))
    age = db.Column(db.Integer)
    activities = db.Column(db.Text)
    duration = db.Column(db.Integer)
    weather = db.Column(db.Text)
    recommendations = db.Column(db.Text)
    
    # New fields for storing outfit data
    outfit_data = db.Column(db.Text)  # JSON string of outfit images and shopping items
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relationship to User
    user = db.relationship('User', backref=db.backref('trips', lazy=True))
    
    def get_outfit_data(self):
        """Get parsed outfit data as Python dict."""
        if self.outfit_data:
            try:
                return json.loads(self.outfit_data)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_outfit_data(self, data):
        """Set outfit data as JSON string."""
        self.outfit_data = json.dumps(data) if data else None
    
    def __repr__(self):
        return f"Trip('{self.city}', '{self.region}', user_id={self.user_id})"

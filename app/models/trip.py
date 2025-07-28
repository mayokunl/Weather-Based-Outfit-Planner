from app import db
from app.models.user import User

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
    
    # Relationship to User
    user = db.relationship('User', backref=db.backref('trips', lazy=True))
    
    def __repr__(self):
        return f"Trip('{self.city}', '{self.region}', user_id={self.user_id})"

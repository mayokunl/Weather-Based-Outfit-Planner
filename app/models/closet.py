from app import db

class ClosetItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    price = db.Column(db.String(20))
    image_url = db.Column(db.String(300))
    
    def __repr__(self):
        return f"ClosetItem('{self.title}', user_id={self.user_id})"

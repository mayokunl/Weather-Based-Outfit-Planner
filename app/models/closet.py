from app import db

class ClosetItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    price = db.Column(db.String(20))
    image_url = db.Column(db.String(300))
    item_type = db.Column(db.String(50))  # e.g., "top", "bottom", "shoes", "accessories"
    source = db.Column(db.String(50))    # Store name
    
    # Add unique constraint to prevent exact duplicates
    __table_args__ = (db.UniqueConstraint('user_id', 'title', 'source', name='unique_user_item'),)
    
    def __repr__(self):
        return f"ClosetItem('{self.title}', type='{self.item_type}', user_id={self.user_id})"

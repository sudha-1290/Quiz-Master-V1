from app.extensions import db
from datetime import datetime

class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    earned_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    badge_icon = db.Column(db.String(50), nullable=False) 
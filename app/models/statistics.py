from app.extensions import db
from datetime import datetime

class UserStatistics(db.Model):
    __tablename__ = 'user_statistics'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_quizzes_taken = db.Column(db.Integer, default=0)
    total_score = db.Column(db.Float, default=0.0)
    average_score = db.Column(db.Float, default=0.0)
    highest_score = db.Column(db.Float, default=0.0)
    total_time_spent = db.Column(db.Integer, default=0)  # in minutes
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    # Add relationship to User model
    user = db.relationship('User', backref='statistics', uselist=False) 
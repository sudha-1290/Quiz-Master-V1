from app.extensions import db
from datetime import datetime

class UserProgress(db.Model):
    __tablename__ = 'user_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    completed_quizzes = db.Column(db.Integer, default=0)
    mastery_level = db.Column(db.String(20), default='beginner')
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='progress')
    subject = db.relationship('Subject', backref='user_progress') 
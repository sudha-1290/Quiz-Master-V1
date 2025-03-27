from app.extensions import db
from datetime import datetime

class Quiz(db.Model):
    __tablename__ = 'quiz'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # in minutes
    total_marks = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Add new columns with consistent naming
    difficulty = db.Column(db.String(20), default='intermediate')  # Changed from difficulty_level
    category = db.Column(db.String(50))
    is_public = db.Column(db.Boolean, default=True)
    time_limit_enforced = db.Column(db.Boolean, default=True)
    passing_percentage = db.Column(db.Float, default=60.0)
    allow_review = db.Column(db.Boolean, default=True)

    # Define relationships
    subject = db.relationship('Subject', backref='quizzes')
    questions = db.relationship('Question', backref='quiz', lazy=True)
    scores = db.relationship('Score', backref='quiz', lazy=True)

    # Add constants for difficulty levels
    DIFFICULTY_LEVELS = ['beginner', 'intermediate', 'advanced', 'expert']

    CATEGORIES = ['Programming', 'Mathematics', 'Science', 'General Knowledge']
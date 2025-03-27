from app.extensions import db
from datetime import datetime

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    attempt_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Remove the duplicate relationship definition
    # user = db.relationship('User', backref='scores')  # Remove this line 
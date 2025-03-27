from flask import Flask
from config import Config
from app.extensions import db, login_manager, mail
# Import all models
from app.models.user import User
from app.models.subject import Subject
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.score import Score
from app.models.achievement import Achievement
from datetime import datetime

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # Add custom template filters
    @app.template_filter('strftime')
    def _jinja2_filter_datetime(date, fmt=None):
        if fmt is None:
            fmt = '%Y-%m-%d %H:%M'
        return date.strftime(fmt) if date else ''

    # Import and register blueprints
    from app.routes import auth_bp, admin_bp, user_bp, main_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)

    return app 
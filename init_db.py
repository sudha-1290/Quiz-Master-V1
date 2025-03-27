from app import create_app, db
from app.models.user import User
from app.models.subject import Subject
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.score import Score
from app.models.achievement import Achievement
from app.models.statistics import UserStatistics
from app.models.feedback import QuizFeedback
from app.models.study_material import StudyMaterial
from app.models.progress import UserProgress
from datetime import datetime
import os
from sqlalchemy import inspect

def init_db():
    app = create_app()
    
    with app.app_context():
        # Drop all existing tables
        db.drop_all()
        print("Dropped all existing tables.")
        
        # Create all tables
        db.create_all()
        print("Created all tables.")
        
        # Create admin user
        admin = User(
            email='admin@quizmaster.com',
            full_name='Admin User',
            is_admin=True,
            created_at=datetime.utcnow()
        )
        admin.set_password('admin123')
        db.session.add(admin)
        print("Created admin user.")
        
        # Create sample subjects
        subjects = [
            Subject(name='Python Programming', 
                   description='Learn Python programming basics and advanced concepts'),
            Subject(name='Mathematics', 
                   description='Essential mathematics concepts and problem solving'),
            Subject(name='Science', 
                   description='General science topics and principles')
        ]
        for subject in subjects:
            db.session.add(subject)
        print("Added sample subjects.")
        
        try:
            db.session.commit()
            
            # Create sample quizzes
            quizzes = [
                Quiz(
                    title='Python Basics',
                    subject_id=1,
                    duration=30,
                    total_marks=100,
                    difficulty='beginner',
                    category='Programming',
                    is_public=True,
                    time_limit_enforced=True,
                    passing_percentage=60.0,
                    allow_review=True
                ),
                Quiz(
                    title='Advanced Python',
                    subject_id=1,
                    duration=45,
                    total_marks=100,
                    difficulty='advanced',
                    category='Programming',
                    is_public=True,
                    time_limit_enforced=True,
                    passing_percentage=70.0,
                    allow_review=True
                ),
                Quiz(
                    title='Basic Mathematics',
                    subject_id=2,
                    duration=30,
                    total_marks=50,
                    difficulty='beginner',
                    category='Mathematics',
                    is_public=True,
                    time_limit_enforced=True,
                    passing_percentage=50.0,
                    allow_review=True
                )
            ]
            
            for quiz in quizzes:
                db.session.add(quiz)
            print("Added sample quizzes.")
            
            db.session.commit()
            
            # Add sample questions
            questions = [
                # Python Basics Quiz Questions
                Question(
                    quiz_id=1,
                    question_text='What is Python?',
                    option1='A programming language',
                    option2='A snake',
                    option3='A database',
                    option4='An operating system',
                    correct_answer=1,
                    marks=10
                ),
                Question(
                    quiz_id=1,
                    question_text='Which of these is a valid Python variable name?',
                    option1='2variable',
                    option2='my-var',
                    option3='my_variable',
                    option4='my variable',
                    correct_answer=3,
                    marks=10
                ),
                # Advanced Python Quiz Questions
                Question(
                    quiz_id=2,
                    question_text='What is a decorator in Python?',
                    option1='A function that takes another function as argument',
                    option2='A class method',
                    option3='A variable type',
                    option4='A loop structure',
                    correct_answer=1,
                    marks=10
                ),
                # Mathematics Quiz Questions
                Question(
                    quiz_id=3,
                    question_text='What is 5 + 7?',
                    option1='10',
                    option2='11',
                    option3='12',
                    option4='13',
                    correct_answer=3,
                    marks=10
                )
            ]
            
            for question in questions:
                db.session.add(question)
            print("Added sample questions.")
            
            # Create study materials
            create_study_materials()
            
            # Create necessary directories if they don't exist
            directories = [
                'app/static/uploads',
                'app/static/profile_pics',
                'app/static/reports'
            ]
            
            for directory in directories:
                if not os.path.exists(directory):
                    os.makedirs(directory)
            print("Created necessary directories.")
            
            db.session.commit()
            print("Database initialized successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error during database initialization: {str(e)}")
            raise e

def create_study_materials():
    materials = [
        {
            'subject_id': 1,  # Make sure this matches an existing subject ID
            'title': 'Introduction to Python',
            'content': 'Basic concepts and syntax of Python programming...',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        # Add more sample study materials as needed
    ]
    
    for material_data in materials:
        material = StudyMaterial(**material_data)
        db.session.add(material)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error creating study materials: {e}")

if __name__ == '__main__':
    print("Starting database initialization...")
    init_db() 
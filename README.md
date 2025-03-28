# Quiz Master - Interactive Learning Platform

## Overview
Quiz Master is a comprehensive web-based learning platform that allows administrators to create and manage quizzes while enabling users to take quizzes, track their progress, and compete on leaderboards. Built with Flask and modern web technologies, it provides an intuitive interface for both administrators and learners.

## Features

### For Administrators
- **Dashboard**: Overview of platform statistics and recent activities
- **Subject Management**: Create, edit, and organize subjects
- **Quiz Management**: Create and manage quizzes with customizable settings
  - Multiple difficulty levels
  - Time limits
  - Passing percentages
  - Public/Private visibility
- **Question Bank**: Add, edit, and manage questions for each quiz
- **Study Materials**: Upload and manage learning resources
- **Analytics**: Detailed insights into user performance and engagement
- **User Management**: Monitor user progress and activities

### For Users
- **Interactive Dashboard**: Personal overview of available quizzes and progress
- **Quiz Taking**: User-friendly interface for attempting quizzes
- **Progress Tracking**: Visual representation of learning progress
- **Performance Analytics**: Detailed statistics of quiz attempts
- **Leaderboard**: Compete with other users
- **Achievement System**: Earn badges for accomplishments
- **Study Resources**: Access to subject-wise study materials

## Technical Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLAlchemy with SQLite
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF
- **Email**: Flask-Mail

### Frontend
- **Framework**: Bootstrap 5
- **Icons**: Font Awesome 6
- **Charts**: Chart.js
- **Fonts**: Google Fonts (Nunito)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/sudha-1290/Quiz-Master.git
cd Quiz-Master
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
export FLASK_APP=run.py
export FLASK_ENV=development
```

5. Initialize the database:
```bash
python init_db.py
```

6. Run the application:
```bash
flask run
```

## Project Structure
```
quiz_master/
├── app/
│   ├── models/
│   │   ├── achievement.py
│   │   ├── question.py
│   │   ├── quiz.py
│   │   ├── score.py
│   │   ├── subject.py
│   │   └── user.py
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── uploads/
│   ├── templates/
│   │   ├── admin/
│   │   ├── auth/
│   │   └── user/
│   ├── __init__.py
│   ├── extensions.py
│   ├── forms.py
│   └── routes.py
├── instance/
├── tests/
├── venv/
├── .gitignore
├── config.py
├── requirements.txt
└── run.py
```

## Configuration

Create a `config.py` file in the instance folder with the following settings:
```python
SECRET_KEY = 'your-secret-key'
SQLALCHEMY_DATABASE_URI = 'sqlite:///quiz_master.db'
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'your-email@gmail.com'
MAIL_PASSWORD = 'your-app-password'
UPLOAD_FOLDER = 'app/static/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt'}
```

## Usage

### Administrator Account
- Email: admin@quizmaster.com
- Password: admin123

### Regular User
1. Register a new account
2. Log in with your credentials
3. Browse available quizzes
4. Track your progress
5. View your position on the leaderboard

## Contributing
1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## Testing
Run the test suite:
```bash
python -m pytest
```

## Security Features
- Password hashing using werkzeug.security
- CSRF protection
- Secure file uploads
- Role-based access control
- Session management
- Password reset functionality


## Acknowledgments
- Flask documentation and community
- Bootstrap team
- Font Awesome
- Chart.js team



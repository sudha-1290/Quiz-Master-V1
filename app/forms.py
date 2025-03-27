from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, SubmitField, TextAreaField, SelectField, IntegerField, FileField, BooleanField, FloatField, EmailField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional, NumberRange
from app.models.user import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Length(max=120)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    full_name = StringField('Full Name', validators=[
        DataRequired(),
        Length(max=100)
    ])
    qualification = StringField('Qualification', validators=[Optional()])
    dob = DateField('Date of Birth', validators=[Optional()])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.')

class SubjectForm(FlaskForm):
    name = StringField('Subject Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Add Subject')

class ChapterForm(FlaskForm):
    name = StringField('Chapter Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    subject_id = SelectField('Subject', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save Chapter')

class QuizForm(FlaskForm):
    title = StringField('Quiz Title', validators=[DataRequired(), Length(min=3, max=100)])
    duration = IntegerField('Duration (minutes)', validators=[DataRequired(), NumberRange(min=1)])
    total_marks = IntegerField('Total Marks', validators=[DataRequired(), NumberRange(min=1)])
    difficulty = SelectField('Difficulty Level', 
                           choices=[('easy', 'Easy'), 
                                  ('medium', 'Medium'), 
                                  ('hard', 'Hard')],
                           validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired(), Length(max=50)])
    passing_percentage = IntegerField('Passing Percentage', 
                                    validators=[DataRequired(), 
                                              NumberRange(min=1, max=100)])
    is_public = BooleanField('Make Quiz Public')
    time_limit_enforced = BooleanField('Enforce Time Limit')
    allow_review = BooleanField('Allow Review After Submission')
    submit = SubmitField('Create Quiz')

class QuestionForm(FlaskForm):
    question_text = TextAreaField('Question', validators=[DataRequired()])
    option1 = StringField('Option 1', validators=[DataRequired()])
    option2 = StringField('Option 2', validators=[DataRequired()])
    option3 = StringField('Option 3', validators=[DataRequired()])
    option4 = StringField('Option 4', validators=[DataRequired()])
    correct_answer = SelectField('Correct Answer', 
                               choices=[(1, 'Option 1'), (2, 'Option 2'), 
                                      (3, 'Option 3'), (4, 'Option 4')],
                               coerce=int,
                               validators=[DataRequired()])
    marks = IntegerField('Marks', validators=[DataRequired()])
    submit = SubmitField('Add Question')

class StudyMaterialForm(FlaskForm):
    subject_id = SelectField('Subject', validators=[DataRequired()], coerce=str)
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=200)])
    content = TextAreaField('Content', validators=[DataRequired()])
    file = FileField('Upload File')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField(
        'Confirm Password', 
        validators=[DataRequired(), EqualTo('password')]
    )
    submit = SubmitField('Reset Password')

class FeedbackForm(FlaskForm):
    rating = SelectField('Rating', 
                        choices=[(1, '1 Star'), (2, '2 Stars'), 
                                (3, '3 Stars'), (4, '4 Stars'), 
                                (5, '5 Stars')],
                        coerce=int,
                        validators=[DataRequired()])
    comment = TextAreaField('Comment', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Submit Feedback')

class UpdateProfileForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    qualification = StringField('Qualification')
    dob = DateField('Date of Birth')
    profile_picture = FileField('Profile Picture')
    submit = SubmitField('Update Profile')

class SearchForm(FlaskForm):
    query = StringField('Search')
    category = SelectField('Category', choices=[
        ('', 'All Categories'),
        ('Programming', 'Programming'),
        ('Mathematics', 'Mathematics'),
        ('Science', 'Science')
    ])
    difficulty = SelectField('Difficulty', choices=[
        ('', 'All Levels'),
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ])
    submit = SubmitField('Search')

class AdminProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    email = EmailField('Email', validators=[DataRequired(), Email(), Length(max=120)])

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters long'),
        EqualTo('confirm_password', message='Passwords must match')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired()]) 
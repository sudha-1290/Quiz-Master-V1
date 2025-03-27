from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import login_user, logout_user, current_user, login_required
from functools import wraps
from app.forms import LoginForm, RegistrationForm, SubjectForm, QuizForm, QuestionForm, ResetPasswordRequestForm, StudyMaterialForm, ResetPasswordForm, UpdateProfileForm, AdminProfileForm, ChangePasswordForm
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
from app.extensions import db, mail
from datetime import datetime, timedelta
from flask_mail import Message
import secrets
import os
from werkzeug.utils import secure_filename
from sqlalchemy import distinct

# Create blueprints
auth_bp = Blueprint('auth', __name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
user_bp = Blueprint('user', __name__, url_prefix='/user')
main_bp = Blueprint('main', __name__)

# Main routes
@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('user.dashboard'))
    return redirect(url_for('auth.login'))

# Authentication routes
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Remove the initial redirect check to prevent loops
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                # Get the next page from the URL parameters
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                if user.is_admin:
                    return redirect(url_for('admin.dashboard'))
                return redirect(url_for('user.dashboard'))
            flash('Invalid email or password', 'danger')
        except Exception as e:
            flash(f'Login error: {str(e)}', 'danger')
            print(f"Login error: {str(e)}")
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User(
                email=form.email.data,
                full_name=form.full_name.data,
                qualification=form.qualification.data,
                dob=form.dob.data,
                created_at=datetime.utcnow()
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Registration failed: {str(e)}', 'danger')
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = secrets.token_urlsafe(32)
            user.reset_token = token
            user.reset_token_expiration = datetime.utcnow() + timedelta(hours=24)
            db.session.commit()
            
            # Send email
            msg = Message('Password Reset Request',
                        sender='noreply@quizmaster.com',
                        recipients=[user.email])
            msg.body = f'''To reset your password, visit the following link:
{url_for('auth.reset_password', token=token, _external=True)}

If you did not make this request then simply ignore this email.
'''
            mail.send(msg)
            
        flash('Check your email for the instructions to reset your password', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', form=form)

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    user = User.verify_reset_token(token)
    if not user:
        flash('Invalid or expired reset token', 'warning')
        return redirect(url_for('auth.reset_password_request'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form)

# Admin route decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('user.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Admin routes
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    total_users = User.query.count()
    total_subjects = Subject.query.count()
    total_quizzes = Quiz.query.count()
    recent_scores = Score.query.order_by(Score.attempt_date.desc()).limit(5).all()
    
    # Calculate average score
    scores = Score.query.all()
    if scores:
        average_score = round(sum(score.score for score in scores) / len(scores), 1)
    else:
        average_score = 0.0
    
    # Get quiz statistics
    quiz_stats = []
    quizzes = Quiz.query.all()
    for quiz in quizzes:
        scores = Score.query.filter_by(quiz_id=quiz.id).all()
        if scores:
            avg_score = sum(score.score for score in scores) / len(scores)
            attempts = len(scores)
        else:
            avg_score = 0
            attempts = 0
        quiz_stats.append([quiz.id, avg_score, attempts])

    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_subjects=total_subjects,
                         total_quizzes=total_quizzes,
                         recent_scores=recent_scores,
                         quiz_stats=quiz_stats,
                         average_score=average_score)

@admin_bp.route('/subjects', methods=['GET', 'POST'])
@admin_required
def manage_subjects():
    form = SubjectForm()
    if form.validate_on_submit():
        subject = Subject(
            name=form.name.data,
            description=form.description.data
        )
        db.session.add(subject)
        db.session.commit()
        flash('Subject added successfully!', 'success')
        return redirect(url_for('admin.manage_subjects'))
    
    subjects = Subject.query.all()
    return render_template('admin/subjects.html', form=form, subjects=subjects)

@admin_bp.route('/subject/<int:subject_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    form = SubjectForm(obj=subject)
    
    if form.validate_on_submit():
        subject.name = form.name.data
        subject.description = form.description.data
        db.session.commit()
        flash('Subject updated successfully!', 'success')
        return redirect(url_for('admin.manage_subjects'))
        
    return render_template('admin/edit_subject.html', form=form, subject=subject)

@admin_bp.route('/subject/<int:subject_id>/delete', methods=['POST'])
@admin_required
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    try:
        db.session.delete(subject)
        db.session.commit()
        flash('Subject deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Cannot delete subject with associated quizzes.', 'danger')
    
    return redirect(url_for('admin.manage_subjects'))

@admin_bp.route('/subject/<int:subject_id>/quizzes')
@admin_required
def subject_quizzes(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    quizzes = Quiz.query.filter_by(subject_id=subject_id).all()
    return render_template('admin/subject_quizzes.html', subject=subject, quizzes=quizzes)

@admin_bp.route('/quiz/<int:quiz_id>/questions', methods=['GET', 'POST'])
@admin_required
def add_questions(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    form = QuestionForm()
    
    if form.validate_on_submit():
        question = Question(
            quiz_id=quiz_id,
            question_text=form.question_text.data,
            option1=form.option1.data,
            option2=form.option2.data,
            option3=form.option3.data,
            option4=form.option4.data,
            correct_answer=form.correct_answer.data,
            marks=form.marks.data
        )
        db.session.add(question)
        db.session.commit()
        flash('Question added successfully!', 'success')
        return redirect(url_for('admin.add_questions', quiz_id=quiz_id))
    
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template('admin/questions.html', 
                         form=form, 
                         quiz=quiz, 
                         questions=questions)

@admin_bp.route('/study-materials', methods=['GET', 'POST'])
@admin_required
def manage_study_materials():
    form = StudyMaterialForm()
    form.subject_id.choices = [(str(s.id), s.name) for s in Subject.query.all()]
    
    if form.validate_on_submit():
        material = StudyMaterial(
            subject_id=int(form.subject_id.data),
            title=form.title.data,
            content=form.content.data
        )
        if form.file.data:
            file = form.file.data
            filename = secure_filename(file.filename)
            file.save(os.path.join('app/static/uploads', filename))
            material.file_path = filename
            
        db.session.add(material)
        db.session.commit()
        flash('Study material added successfully!', 'success')
        return redirect(url_for('admin.manage_study_materials'))
        
    materials = StudyMaterial.query.all()
    return render_template('admin/study_materials.html', form=form, materials=materials)

@admin_bp.route('/subject/<int:subject_id>/quiz/create', methods=['GET', 'POST'])
@admin_required
def create_quiz(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    form = QuizForm()
    
    if form.validate_on_submit():
        try:
            quiz = Quiz(
                title=form.title.data,
                subject_id=subject_id,
                duration=form.duration.data,
                total_marks=form.total_marks.data,
                difficulty=form.difficulty.data,
                category=form.category.data,
                passing_percentage=form.passing_percentage.data,
                is_public=form.is_public.data,
                time_limit_enforced=form.time_limit_enforced.data,
                allow_review=form.allow_review.data
            )
            db.session.add(quiz)
            db.session.commit()
            flash('Quiz created successfully!', 'success')
            return redirect(url_for('admin.subject_quizzes', subject_id=subject_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating quiz: {str(e)}', 'danger')
            
    return render_template('admin/create_quiz.html', form=form, subject=subject)

# User routes
@user_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
        
    try:
        available_quizzes = Quiz.query.all()
        completed_quizzes = Score.query.filter_by(user_id=current_user.id).all()
        achievements = Achievement.query.filter_by(user_id=current_user.id).all()
        
        return render_template('user/dashboard.html',
                             available_quizzes=available_quizzes,
                             completed_quizzes=completed_quizzes,
                             achievements=achievements)
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'danger')
        return redirect(url_for('auth.login'))

@user_bp.route('/quiz/<int:quiz_id>')
@login_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template('user/take_quiz.html', 
                         quiz=quiz, 
                         questions=questions)

@user_bp.route('/quiz/<int:quiz_id>/submit', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    try:
        quiz = Quiz.query.get_or_404(quiz_id)
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        
        if not questions:
            flash('No questions found for this quiz.', 'danger')
            return redirect(url_for('user.dashboard'))
        
        score = 0
        total_marks = 0
        
        # Calculate score
        for question in questions:
            answer = request.form.get(f'question_{question.id}')
            if answer and answer == str(question.correct_answer):
                score += question.marks
            total_marks += question.marks
        
        percentage = (score / total_marks) * 100 if total_marks > 0 else 0
        
        # Save score
        quiz_score = Score(
            user_id=current_user.id,
            quiz_id=quiz_id,
            score=percentage,
            attempt_date=datetime.utcnow()
        )
        db.session.add(quiz_score)
        db.session.commit()  # Commit the score first
        
        # Get or create user statistics
        stats = UserStatistics.query.filter_by(user_id=current_user.id).first()
        if not stats:
            stats = UserStatistics(
                user_id=current_user.id,
                total_quizzes_taken=0,
                total_score=0,
                average_score=0,
                highest_score=0,
                total_time_spent=0
            )
            db.session.add(stats)
        
        # Update statistics
        stats.total_quizzes_taken += 1
        stats.total_score += percentage
        stats.average_score = stats.total_score / stats.total_quizzes_taken
        stats.highest_score = max(stats.highest_score or 0, percentage)
        stats.total_time_spent += quiz.duration
        stats.last_updated = datetime.utcnow()
        
        # Get or create user progress
        progress = UserProgress.query.filter_by(
            user_id=current_user.id,
            subject_id=quiz.subject_id
        ).first()
        
        if not progress:
            progress = UserProgress(
                user_id=current_user.id,
                subject_id=quiz.subject_id,
                completed_quizzes=0,
                mastery_level='beginner',
                last_activity=datetime.utcnow()
            )
            db.session.add(progress)
        
        # Update progress
        progress.completed_quizzes += 1
        progress.last_activity = datetime.utcnow()
        
        # Update mastery level based on average score
        if stats.average_score >= 90:
            progress.mastery_level = 'expert'
        elif stats.average_score >= 75:
            progress.mastery_level = 'advanced'
        elif stats.average_score >= 60:
            progress.mastery_level = 'intermediate'
        else:
            progress.mastery_level = 'beginner'
        
        db.session.commit()
        
        # Check for achievements
        check_achievements(current_user.id, percentage)
        
        flash(f'Quiz submitted successfully! Your score: {percentage:.2f}%', 'success')
        return redirect(url_for('user.view_result', score_id=quiz_score.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error submitting quiz: {str(e)}', 'danger')
        return redirect(url_for('user.dashboard'))

def check_achievements(user_id, score):
    try:
        # Check for "Perfect Score" achievement
        if score == 100:
            achievement = Achievement.query.filter_by(
                user_id=user_id,
                name="Perfect Score"
            ).first()
            
            if not achievement:
                new_achievement = Achievement(
                    user_id=user_id,
                    name="Perfect Score",
                    description="Scored 100% on a quiz!",
                    earned_date=datetime.utcnow(),
                    badge_icon="fa-star"
                )
                db.session.add(new_achievement)
        
        # Check for "Quiz Master" achievement (5 scores >= 80%)
        high_scores = Score.query.filter(
            Score.user_id == user_id,
            Score.score >= 80
        ).count()
        
        if high_scores >= 5:
            achievement = Achievement.query.filter_by(
                user_id=user_id,
                name="Quiz Master"
            ).first()
            
            if not achievement:
                new_achievement = Achievement(
                    user_id=user_id,
                    name="Quiz Master",
                    description="Scored 80% or higher on 5 quizzes!",
                    earned_date=datetime.utcnow(),
                    badge_icon="fa-crown"
                )
                db.session.add(new_achievement)
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        print(f"Error checking achievements: {str(e)}")

@user_bp.route('/quiz/result/<int:score_id>')
@login_required
def view_result(score_id):
    try:
        score = Score.query.get_or_404(score_id)
        
        # Ensure user can only view their own results
        if score.user_id != current_user.id:
            flash('Access denied.', 'danger')
            return redirect(url_for('user.dashboard'))
        
        # Ensure quiz relationship is loaded
        if not score.quiz:
            flash('Quiz details not found.', 'warning')
        
        return render_template('user/quiz_result.html', score=score)
        
    except Exception as e:
        flash(f'Error loading quiz result: {str(e)}', 'danger')
        return redirect(url_for('user.dashboard'))

@user_bp.route('/progress')
@login_required
def view_progress():
    try:
        # Calculate overall statistics
        user_scores = Score.query.filter_by(user_id=current_user.id).all()
        
        stats = {
            'total_quizzes_taken': len(user_scores),
            'average_score': 0.0,
            'highest_score': 0.0,
            'total_time_spent': 0
        }
        
        if user_scores:
            scores = [score.score for score in user_scores]
            stats['average_score'] = sum(scores) / len(scores)
            stats['highest_score'] = max(scores)
            # Calculate total time spent using quiz durations instead of score time_taken
            stats['total_time_spent'] = sum(score.quiz.duration for score in user_scores if score.quiz)

        # Calculate subject performance
        subject_performance = []
        subjects = Subject.query.all()
        
        for subject in subjects:
            subject_scores = []
            for quiz in subject.quizzes:
                scores = Score.query.filter_by(
                    user_id=current_user.id,
                    quiz_id=quiz.id
                ).all()
                if scores:
                    subject_scores.extend([score.score for score in scores])
            
            if subject_scores:
                avg_score = sum(subject_scores) / len(subject_scores)
                subject_performance.append([subject.name, avg_score])

        # Calculate progress by subject
        progress_data = []
        for subject in subjects:
            completed_quizzes = Score.query.filter(
                Score.user_id == current_user.id,
                Score.quiz_id.in_([quiz.id for quiz in subject.quizzes])
            ).distinct(Score.quiz_id).count()
            
            # Calculate mastery level based on average score
            subject_scores = []
            for quiz in subject.quizzes:
                best_score = Score.query.filter_by(
                    user_id=current_user.id,
                    quiz_id=quiz.id
                ).order_by(Score.score.desc()).first()
                if best_score:
                    subject_scores.append(best_score.score)
            
            avg_subject_score = sum(subject_scores) / len(subject_scores) if subject_scores else 0
            
            if avg_subject_score >= 90:
                mastery_level = "Expert"
            elif avg_subject_score >= 75:
                mastery_level = "Advanced"
            elif avg_subject_score >= 60:
                mastery_level = "Intermediate"
            else:
                mastery_level = "Beginner"
            
            progress_data.append({
                'subject': subject,
                'completed_quizzes': completed_quizzes,
                'mastery_level': mastery_level
            })

        return render_template('user/progress.html',
                             stats=stats,
                             subject_performance=subject_performance,
                             progress_data=progress_data)

    except Exception as e:
        flash(f'Error loading progress: {str(e)}', 'danger')
        return redirect(url_for('user.dashboard'))

@user_bp.route('/search')
@login_required
def user_search():
    query = request.args.get('q', '')
    subject_id = request.args.get('subject', '')
    difficulty = request.args.get('difficulty', '')
    
    quizzes = Quiz.query.filter(Quiz.is_public == True)
    subjects = Subject.query.all()
    
    if query:
        quizzes = quizzes.filter(Quiz.title.ilike(f'%{query}%'))
    if subject_id:
        quizzes = quizzes.filter(Quiz.subject_id == subject_id)
    if difficulty:
        quizzes = quizzes.filter(Quiz.difficulty == difficulty)
    
    quizzes = quizzes.all()
    
    return render_template('user/search_results.html',
                         quizzes=quizzes,
                         subjects=subjects,
                         query=query,
                         selected_subject=subject_id,
                         selected_difficulty=difficulty)

@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        current_user.full_name = form.full_name.data
        current_user.qualification = form.qualification.data
        current_user.dob = form.dob.data
        
        if form.profile_picture.data:
            file = form.profile_picture.data
            filename = secure_filename(file.filename)
            file.save(os.path.join('app/static/profile_pics', filename))
            current_user.profile_picture = filename
            
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user.profile'))
        
    elif request.method == 'GET':
        form.full_name.data = current_user.full_name
        form.qualification.data = current_user.qualification
        form.dob.data = current_user.dob
        
    return render_template('user/profile.html', form=form)

@user_bp.route('/quiz/<int:quiz_id>/review/<int:score_id>')
@login_required
def review_quiz(quiz_id, score_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    score = Score.query.get_or_404(score_id)
    
    if score.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('user.dashboard'))
    
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    user_answers = score.get_answers()  # You'll need to add this method to Score model
    
    return render_template('user/review_quiz.html',
                         quiz=quiz,
                         score=score,
                         questions=questions,
                         user_answers=user_answers)

@user_bp.route('/export/results')
@login_required
def export_results():
    from fpdf import FPDF
    
    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Add header
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Quiz Results Report', 0, 1, 'C')
    
    # Add user info
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Name: {current_user.full_name}', 0, 1)
    pdf.cell(0, 10, f'Email: {current_user.email}', 0, 1)
    
    # Add quiz results
    scores = Score.query.filter_by(user_id=current_user.id)\
                       .order_by(Score.attempt_date.desc()).all()
    
    for score in scores:
        pdf.cell(0, 10, f'Quiz: {score.quiz.title}', 0, 1)
        pdf.cell(0, 10, f'Score: {score.score}%', 0, 1)
        pdf.cell(0, 10, f'Date: {score.attempt_date.strftime("%Y-%m-%d")}', 0, 1)
        pdf.ln(5)
    
    # Save PDF
    pdf_path = f'app/static/reports/results_{current_user.id}.pdf'
    pdf.output(pdf_path)
    
    return send_file(pdf_path, as_attachment=True)

@admin_bp.route('/analytics')
@admin_required
def quiz_analytics():
    try:
        # Calculate total attempts
        total_attempts = Score.query.count()

        # Calculate average score
        scores = Score.query.all()
        avg_score = 0.0
        if scores:
            avg_score = round(sum(score.score for score in scores) / len(scores), 1)

        # Get subject statistics
        subject_stats = []
        subjects = Subject.query.all()
        for subject in subjects:
            quizzes = Quiz.query.filter_by(subject_id=subject.id).all()
            subject_attempts = 0
            subject_total_score = 0
            for quiz in quizzes:
                quiz_scores = Score.query.filter_by(quiz_id=quiz.id).all()
                subject_attempts += len(quiz_scores)
                if quiz_scores:
                    subject_total_score += sum(score.score for score in quiz_scores)
            
            avg_subject_score = 0
            if subject_attempts > 0:
                avg_subject_score = round(subject_total_score / subject_attempts, 1)
            
            subject_stats.append([subject.name, subject_attempts, avg_subject_score])

        # Get user engagement data (last 30 days)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        engagement_data = []
        for i in range(30):
            date = thirty_days_ago + timedelta(days=i)
            next_date = date + timedelta(days=1)
            daily_attempts = Score.query.filter(
                Score.attempt_date >= date,
                Score.attempt_date < next_date
            ).count()
            engagement_data.append([date.strftime('%Y-%m-%d'), daily_attempts])

        return render_template('admin/analytics.html',
                             total_attempts=total_attempts,
                             avg_score=avg_score,
                             subject_stats=subject_stats,
                             user_engagement=engagement_data)

    except Exception as e:
        flash(f'Error loading analytics: {str(e)}', 'danger')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/quiz/<int:quiz_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    form = QuizForm(obj=quiz)
    
    if form.validate_on_submit():
        try:
            quiz.title = form.title.data
            quiz.duration = form.duration.data
            quiz.total_marks = form.total_marks.data
            quiz.difficulty = form.difficulty.data
            quiz.category = form.category.data
            quiz.passing_percentage = form.passing_percentage.data
            quiz.is_public = form.is_public.data
            quiz.time_limit_enforced = form.time_limit_enforced.data
            quiz.allow_review = form.allow_review.data
            
            db.session.commit()
            flash('Quiz updated successfully!', 'success')
            return redirect(url_for('admin.subject_quizzes', subject_id=quiz.subject_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating quiz: {str(e)}', 'danger')
    
    return render_template('admin/edit_quiz.html', form=form, quiz=quiz)

@admin_bp.route('/quiz/<int:quiz_id>/questions')
@admin_required
def manage_questions(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template('admin/questions.html', quiz=quiz, questions=questions)

@admin_bp.route('/quiz/<int:quiz_id>/delete', methods=['POST'])
@admin_required
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    subject_id = quiz.subject_id
    
    try:
        # Delete associated questions first
        Question.query.filter_by(quiz_id=quiz_id).delete()
        # Delete associated scores
        Score.query.filter_by(quiz_id=quiz_id).delete()
        # Delete the quiz
        db.session.delete(quiz)
        db.session.commit()
        flash('Quiz deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting quiz: {str(e)}', 'danger')
    
    return redirect(url_for('admin.subject_quizzes', subject_id=subject_id))

@admin_bp.route('/profile', methods=['GET', 'POST'])
@admin_required
def profile():
    form = AdminProfileForm(obj=current_user)
    password_form = ChangePasswordForm()

    if form.validate_on_submit():
        try:
            current_user.first_name = form.first_name.data
            current_user.last_name = form.last_name.data
            current_user.email = form.email.data
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('admin.profile'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'danger')

    return render_template('admin/profile.html', form=form, password_form=password_form)

@admin_bp.route('/change-password', methods=['POST'])
@admin_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            try:
                current_user.set_password(form.new_password.data)
                db.session.commit()
                flash('Password changed successfully!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error changing password: {str(e)}', 'danger')
        else:
            flash('Current password is incorrect!', 'danger')
    return redirect(url_for('admin.profile'))

@user_bp.route('/leaderboard')
@login_required
def leaderboard():
    try:
        # Get all users and their quiz scores
        users = User.query.filter_by(is_admin=False).all()
        top_users = []
        
        for user in users:
            scores = Score.query.filter_by(user_id=user.id).all()
            if scores:
                avg_score = sum(score.score for score in scores) / len(scores)
                quiz_count = len(scores)
                top_users.append((user, avg_score, quiz_count))
        
        # Sort users by average score in descending order
        top_users.sort(key=lambda x: x[1], reverse=True)
        
        # Take top 10 users
        top_users = top_users[:10]
        
        # Add datetime for the template
        from datetime import datetime
        
        return render_template('user/leaderboard.html', 
                             top_users=top_users,
                             datetime=datetime)
                             
    except Exception as e:
        flash(f'Error loading leaderboard: {str(e)}', 'danger')
        return redirect(url_for('user.dashboard'))

@admin_bp.route('/question/<int:question_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)
    form = QuestionForm(obj=question)
    
    if form.validate_on_submit():
        try:
            question.question_text = form.question_text.data
            question.option1 = form.option1.data
            question.option2 = form.option2.data
            question.option3 = form.option3.data
            question.option4 = form.option4.data
            question.correct_answer = form.correct_answer.data
            question.marks = form.marks.data
            
            db.session.commit()
            flash('Question updated successfully!', 'success')
            return redirect(url_for('admin.manage_questions', quiz_id=question.quiz_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating question: {str(e)}', 'danger')
    
    return render_template('admin/edit_question.html', form=form, question=question)

@admin_bp.route('/question/<int:question_id>/delete', methods=['POST'])
@admin_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    quiz_id = question.quiz_id
    
    try:
        db.session.delete(question)
        db.session.commit()
        flash('Question deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting question: {str(e)}', 'danger')
    
    return redirect(url_for('admin.manage_questions', quiz_id=quiz_id))

@admin_bp.route('/search')
@admin_required
def admin_search():
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'all')
    
    results = {
        'subjects': [],
        'quizzes': [],
        'users': []
    }
    
    if query:
        if search_type in ['all', 'subjects']:
            results['subjects'] = Subject.query.filter(
                Subject.name.ilike(f'%{query}%')
            ).all()
            
        if search_type in ['all', 'quizzes']:
            results['quizzes'] = Quiz.query.filter(
                Quiz.title.ilike(f'%{query}%')
            ).all()
            
        if search_type in ['all', 'users']:
            results['users'] = User.query.filter(
                User.full_name.ilike(f'%{query}%')
            ).all()
    
    return render_template('admin/search_results.html', 
                         results=results, 
                         query=query,
                         search_type=search_type)

@user_bp.route('/study-materials')
@login_required
def view_study_materials():
    try:
        # Get all subjects and their study materials
        subjects = Subject.query.all()
        materials_by_subject = {}
        
        for subject in subjects:
            materials = StudyMaterial.query.filter_by(subject_id=subject.id).all()
            if materials:
                materials_by_subject[subject] = materials
        
        return render_template('user/study_materials.html',
                             materials_by_subject=materials_by_subject)
                             
    except Exception as e:
        flash(f'Error loading study materials: {str(e)}', 'danger')
        return redirect(url_for('user.dashboard')) 
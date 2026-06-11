from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, AllowedStudent

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        student_id  = request.form.get('student_id', '').strip()
        email       = request.form.get('email', '').strip().lower()
        name        = request.form.get('name', '').strip()
        password    = request.form.get('password', '')
        nationality = request.form.get('nationality', '').strip()

        if not student_id or not email or not name or not password:
            flash('Please fill in all required fields.', 'danger')
            return render_template('auth/register.html')

        if not student_id.isdigit() or len(student_id) != 8:
            flash('Student ID must be exactly 8 digits.', 'danger')
            return render_template('auth/register.html')

        if not AllowedStudent.query.filter_by(student_id=student_id).first():
            flash('That student ID is not on the programme list. Please contact OIA if you think this is an error.', 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(student_id=student_id).first():
            flash('An account for that student ID already exists.', 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('An account with that email already exists.', 'danger')
            return render_template('auth/register.html')

        user = User(email=email, name=name, nationality=nationality,
                    role='student', student_id=student_id)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash(f'Welcome to Li-Ze Academy, {user.name}!', 'success')
        return redirect(url_for('student.dashboard'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_staff:
            return redirect(url_for('staff.dashboard'))
        return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            if user.is_staff:
                return redirect(next_page or url_for('staff.dashboard'))
            return redirect(next_page or url_for('student.dashboard'))

        flash('Incorrect email or password.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('public.home'))

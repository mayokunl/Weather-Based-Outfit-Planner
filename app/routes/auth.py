from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models.user import User
from app.forms import RegistrationForm, LoginForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if user and check_password_hash(user.password, form.password.data):
                login_user(user)
                # Remove redundant session storage - Flask-Login handles this
                return redirect(url_for('main.home'))
            else:
                raise ValueError("Invalid Email/Password")
        except Exception as e:
            return render_template('login.html', form=form, message=e)
    return render_template('login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user_exists = User.query.filter_by(username=form.username.data).first()
        email_exists = User.query.filter_by(email=form.email.data).first()
        if user_exists or email_exists:
            flash('User or email already exists.', 'error')
            return render_template('register.html', form=form)
        hashed_pw = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        # Remove redundant session storage - Flask-Login handles this
        return redirect(url_for('auth.complete_profile'))
    return render_template('register.html', form=form)

@auth_bp.route('/completeProfile', methods=['GET', 'POST'])
@login_required
def complete_profile():
    if request.method == 'POST':
        current_user.name = request.form['name']
        current_user.age = request.form['age']
        current_user.gender = request.form['gender']
        db.session.commit()
        # Store user profile data in session for trip planning
        session['age'] = current_user.age
        session['gender'] = current_user.gender
        return redirect(url_for('main.home'))
    return render_template('completeProfile.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

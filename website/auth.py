from flask import Blueprint, render_template, url_for, request, flash, redirect, abort
from .models import db, User, Role
from .utils import bcrypt
from datetime import datetime
from flask_login import login_user, current_user, login_required, logout_user
from . import csrf, limiter
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

auth = Blueprint('auth', __name__)

# Add rate limiting to prevent brute force attacks
limiter.limit("5 per minute")(auth)

# Serializer for generating secure tokens
serializer = URLSafeTimedSerializer("jkjklolggyoudontevenknowhowtobegaydude")

def generate_password_change_url(user):
    token = serializer.dumps(user.user_id)
    return url_for('auth.auth_change_password', token=token, _external=True)

@auth.route('/', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def auth_login():
    if request.method == 'POST':
        email = request.form.get('email-fr-usr', '').strip()
        password = request.form.get('password-fr-usr', '').strip()

        if not email or not password:
            flash('Email and password are required.', 'error')
            return redirect(url_for('auth.auth_login'))

        user_to_login = User.query.filter_by(email=email).first()

        if user_to_login:
            if not user_to_login.is_active:
                flash('Invalid email or password.', 'error')
                user_to_login.failed_login_attempts += 1
                db.session.commit()
                return redirect(url_for('auth.auth_login'))

            if user_to_login.failed_login_attempts >= 3:
                user_to_login.is_active = False
                db.session.commit()
                flash('Your account is locked due to failed login attempts.', 'error')
                return redirect(url_for('auth.auth_login'))

            # Check if the password is expired
            if user_to_login.password_last_changed is None or \
                    (datetime.utcnow() - user_to_login.password_last_changed).days > 365:
                # Log in the user
                login_user(user_to_login)

                # Generate a password change token
                token = serializer.dumps(user_to_login.user_id)
                flash('Your password has expired. Please update it.', 'warning')
                return redirect(url_for('auth.auth_change_password', token=token))

            # Validate the password
            if bcrypt.check_password_hash(user_to_login.password, password):
                user_to_login.failed_login_attempts = 0
                user_to_login.last_login = datetime.utcnow()
                db.session.commit()

                login_user(user_to_login)

                # Handle first login logic
                if user_to_login.first_login:
                    user_to_login.first_login = False
                    db.session.commit()

                # Redirect based on role
                if user_to_login.role.role_name == 'admin':
                    return redirect(url_for('admin.admin_welcome' if user_to_login.first_login else 'admin.admin_home'))
                elif user_to_login.role.role_name == 'user':
                    return redirect(url_for('user.user_welcome' if user_to_login.first_login else 'user.user_home'))

                flash('You do not have a valid authority.', 'error')
                return redirect(url_for('auth.auth_login'))
            else:
                user_to_login.failed_login_attempts += 1
                db.session.commit()
                flash('Invalid email or password.', 'error')
                return redirect(url_for('auth.auth_login'))

        flash('Invalid email or password.', 'error')
        return redirect(url_for('auth.auth_login'))

    return render_template('auth-login.html')

@auth.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def auth_register():
    if request.method == 'POST':
        email = request.form.get('email-fr-usr', '').strip()
        password = request.form.get('password-fr-usr', '').strip()
        confirm_password = request.form.get('conf-password-fr-usr', '').strip()
        first_name = request.form.get('first-name-fr-usr', '').strip()
        last_name = request.form.get('last-name-fr-usr', '').strip()

        # Validate inputs
        if not email or not password or not confirm_password or not first_name or not last_name:
            flash('All fields are required.', 'warning')
            return redirect(url_for('auth.auth_register'))

        if password != confirm_password:
            flash('Passwords do not match.', 'warning')
            return redirect(url_for('auth.auth_register'))

        if User.query.filter_by(email=email).first():
            flash('Email is already in use.', 'warning')
            return redirect(url_for('auth.auth_register'))

        # Fetch the role_id for the 'user' role
        user_role = Role.query.filter_by(role_name='user').first()
        if not user_role:
            flash('Default user role not found. Please contact an administrator.', 'error')
            return redirect(url_for('auth.auth_register'))

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create a new user
        new_user = User(
            email=email,
            password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            role_id=user_role.role_id,  # Default to user role
            is_active=True,
            password_last_changed=datetime.utcnow()
        )

        try:
            # Save the user to the database
            db.session.add(new_user)
            db.session.commit()

            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.auth_login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'error')
            print(f"Error: {e}")  # Log the error for debugging
            return redirect(url_for('auth.auth_register'))

    return render_template('auth-register.html')

@auth.route('/change-password/<token>', methods=['GET', 'POST'])
@login_required  # Ensure the user is authenticated
def auth_change_password(token):
    try:
        # Validate the token and extract the user ID
        user_id = serializer.loads(token, max_age=3600)  # Token is valid for 1 hour

        # Ensure the token matches the currently logged-in user
        if current_user.user_id != user_id:
            flash('Unauthorized access.', 'error')
            return redirect(url_for('auth.auth_login'))
    except SignatureExpired:
        flash('Your password change link has expired. Please request a new one.', 'error')
        return redirect(url_for('auth.auth_login'))
    except BadSignature:
        flash('Invalid password change link.', 'error')
        return redirect(url_for('auth.auth_login'))

    if request.method == 'POST':
        # Fetch form data
        current_password = request.form.get('curr-passwd-fr-usr', '').strip()
        new_password = request.form.get('new-passwd-fr-usr', '').strip()
        confirm_password = request.form.get('conf-passwd-fr-usr', '').strip()

        # Validate form inputs
        if not current_password or not new_password or not confirm_password:
            flash('All fields are required.', 'error')
            return redirect(url_for('auth.auth_change_password', token=token))

        if new_password != confirm_password:
            flash('New password and confirmation do not match.', 'error')
            return redirect(url_for('auth.auth_change_password', token=token))

        # Verify the current password
        if not bcrypt.check_password_hash(current_user.password, current_password):
            flash('Current password is incorrect.', 'error')
            return redirect(url_for('auth.auth_change_password', token=token))

        # Hash the new password and update the user record
        current_user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        current_user.password_last_changed = datetime.utcnow()
        db.session.commit()

        flash('Your password has been changed successfully.', 'success')
        return redirect(url_for('auth.auth_login'))

    return render_template('auth-change-password.html', token=token)

@auth.route('/logout', methods=['GET'])
@login_required
def auth_logout():
    # Log out the current user
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.auth_login'))

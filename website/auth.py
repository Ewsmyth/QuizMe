from flask import Blueprint, render_template, url_for, request, flash, redirect
from .models import db, User
from .utils import bcrypt
from datetime import datetime
from flask_login import login_user
from . import csrf, limiter

auth = Blueprint('auth', __name__)

# Add rate limiting to prevent brute force attacks
limiter.limit("5 per minute")(auth)

@auth.route('/', methods=['GET', 'POST'])
@limiter.limit("5 per minute")  # Additional explicit rate limiting
def auth_login():
    if request.method == 'POST':
        email = request.form.get('email-fr-usr', '').strip()  # Sanitize and trim input
        password = request.form.get('password-fr-usr', '').strip()

        # Ensure email and password are provided
        if not email or not password:
            flash('Email and password are required.', 'error')
            return redirect(url_for('auth.auth_login'))

        user_to_login = User.query.filter_by(email=email).first()

        if user_to_login:
            # Check if the account is inactive
            if not user_to_login.is_active:
                flash('Invalid email or password.', 'error')  # Generic error message to prevent enumeration

                # Increment failed login attempts
                user_to_login.failed_login_attempts += 1
                db.session.commit()
                return redirect(url_for('auth.auth_login'))

            # Check for excessive failed login attempts
            if user_to_login.failed_login_attempts >= 3:
                user_to_login.is_active = False  # Lock the account
                db.session.commit()
                flash('Your account has been locked due to multiple failed login attempts.', 'error')
                return redirect(url_for('auth.auth_login'))

            # Check password expiration
            if user_to_login.password_last_changed is None or \
                    (datetime.utcnow() - user_to_login.password_last_changed).days > 365:
                flash('Your password has expired. Please update it.', 'warning')
                return redirect(url_for('auth.auth_change_password'))

            # Validate the password
            if bcrypt.check_password_hash(user_to_login.password, password):
                # Reset failed login attempts and update last login time
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

                # Catch all for invalid roles
                flash('You do not have a valid authority.', 'error')
                return redirect(url_for('auth.auth_login'))
            else:
                # Increment failed login attempts for incorrect password
                user_to_login.failed_login_attempts += 1
                db.session.commit()
                flash('Invalid email or password.', 'error')  # Generic error message
                return redirect(url_for('auth.auth_login'))
        else:
            # Generic error message to prevent user enumeration
            flash('Invalid email or password.', 'error')
            return redirect(url_for('auth.auth_login'))

    return render_template('auth-login.html')

@auth.route('/change-password/')
def auth_change_password():
    return render_template('auth-change-password.html')
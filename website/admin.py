from flask import Blueprint, render_template, url_for, jsonify, request, abort
from .models import db, User, Role
from .utils import bcrypt
from datetime import datetime
from flask_login import current_user, login_required
from . import csrf, limiter
from .decorators import role_required

admin = Blueprint('admin', __name__)

@admin.route('/admin-home/')
@login_required
@role_required('admin')
def admin_home():
    return render_template('admin-home.html')

@admin.route('/admin-welcome/')
@login_required
@role_required('admin')
def admin_welcome():
    return render_template('admin-welcome.html')

@admin.route('/admin-home/users/')
@login_required
@role_required('admin')
def admin_users():
    users = User.query.all()
    return render_template('admin-users.html', user=users)

@admin.route('/admin-home/admin-quizzes')
@login_required
@role_required('admin')
def admin_quizzes():
    return render_template('admin-quizzes.html')

@admin.route('/admin-home/create-user/submit/', methods=['POST'])
@csrf.exempt  # Ensure CSRF is checked
@limiter.limit("5 per minute")  # Prevent abuse
@login_required
@role_required('admin')
def admin_create_user():
    # Ensure current user is admin
    if current_user.role.role_name != 'admin':
        abort(403, description="You are not authorized to perform this action.")

    # Parse form inputs
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()
    role = request.form.get('role', '').strip()
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()

    # Validate required fields
    if not email or not password or not role:
        return jsonify({'error': 'Email, password, and role are required.'}), 400

    if role not in ['admin', 'user']:
        return jsonify({'error': 'Invalid role provided.'}), 400

    # Check if the email already exists
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists.'}), 400

    # Hash the password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Fetch the role ID using the role name
    user_role = Role.query.filter_by(role_name=role).first()
    if not user_role:
        return jsonify({'error': 'Role not found in database.'}), 500

    # Create the new user
    new_user = User(
        email=email,
        password=hashed_password,
        role_id=user_role.role_id,  # Use the role ID for foreign key
        first_name=first_name,
        last_name=last_name,
        created_by=current_user.user_id,  # Reference the admin's user_id
        first_login=True,
        password_last_changed=datetime.utcnow(),
        is_active=True,  # Default new users to active
    )

    # Save to database
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'success': 'User created successfully.'}), 201

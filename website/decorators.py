from functools import wraps
from flask import current_app, redirect, url_for, flash
from flask_login import current_user

def role_required(*roles):
    """Decorator to restrict access based on user roles."""
    def wrapper(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            # Ensure the user is authenticated and has the current role
            if not current_user.is_authenticated or not current_user.role or current_user.role.role_name not in roles:
                print(f"Unauthorized access attempt by user: {current_user.email if current_user.is_authenticated else 'Anonymous'}")
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('auth.auth_login'))
            return func(*args, **kwargs)
        return decorated_view
    return wrapper
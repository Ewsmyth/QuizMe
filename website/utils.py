from flask import current_app
from . import config
from flask_bcrypt import Bcrypt
from .models import db, User, Role
from datetime import timedelta, datetime

bcrypt = Bcrypt()

def create_roles():
    """Creates default roles"""
    try:
        print("Fetching roles...")

        # Check if roles already exist
        admin_role = Role.query.filter_by(role_name='admin').first()
        user_role = Role.query.filter_by(role_name='user').first()

        # Debug output
        print(f"Admin role: {admin_role}")
        print(f"User role: {user_role}")

        # Create admin role if not found
        if not admin_role:
            print("Admin role not found, creating admin role...")
            admin_role = Role(role_name='admin', description='System administrator role with complete system management.')
            db.session.add(admin_role)
            print("Admin role created.")
        else:
            print(f"Admin role found: {admin_role}")

        # Create user role if not found
        if not user_role:
            print("User role not found, creating user role...")
            user_role = Role(role_name='user', description='Standard userrole with limited access.')
            db.session.add(user_role)
            print("User role created.")

        db.session.commit()
        print("Roles committed to database...")

    except Exception as e:
        print(f"Error creating roles: {e}")

def create_admin_user():
    """Creates a user with the admin role"""
    try:
        print("Fetching admin role for admin user creation...")

        # Fetch the admin role
        admin_role = Role.query.filter_by(role_name='admin').first()
        if not admin_role:
            print("Admin role not found. Cannot create admin user.")
            return

        search_for_admin =User.query.filter_by(role_id=admin_role.role_id).first()
        if not search_for_admin:
            print("No admin user found. Creating admin user.")

            password_hash = bcrypt.generate_password_hash('changeme').decode('utf-8')

            create_admin = User(
                email='admin@admin.admin',
                role_id=admin_role.role_id,
                password=password_hash,
                created_by=1,
                is_active=True
            )
            db.session.add(create_admin)
            db.session.commit()
            print("Admin user has been created.")
            print("Admin default email is: admin@admin.admin")
            print("Admin default password is: changeme")
        else:
            print("Admin user already exists.")
    
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.session.rollback()
from flask import current_app
from . import config
from flask_bcrypt import Bcrypt
from .models import db, User, Role
from datetime import timedelta, datetime

bcrypt = Bcrypt()

def create_roles():
    """Creates default roles"""
    try:
        # Check if roles already exist
        admin_role = Role.query.filter_by(role_name='admin').first()
        user_role = Role.query.filter_by(role_name='user').first()

        if not admin_role:
            admi_role = Role(role_name='admin', description='System administrator role with complete system management.')
            db.session.add(admin_role)
            print("Admin role created")

        if not user_role:
            user_role = Role(role_name='user', description='Standard userrole with limited access.')
            db.session.add(user_role)
            print("User role created.")

        db.session.commit()

    except Exception as e:
        print(f"Error creating roles: {e}")

def create_admin_user():
    """Creates a user with the admin role"""
    try:
        # Fetch the admin role
        admin_role = Role.query.filter_by(role_name='admin').first()
        if not admin_role:
            print("Admin role not found.")
            return

        search_for_admin =User.query.filter_by(role_id=admin_role.role_id).first()
        if not search_for_admin:
            print("No admin user found. Creating admin user.")

            password_hash = bcrypt.generate_password_hash('changeme').decode('utf-8')

            create_admin = User(
                email='admin@admin.admin',
                role_id=admin_role.role_id,
                password=password_hash,
                created_by=1
            )
            db.session.add(create_admin)
            db.session.commit()
            print("Admin user has been created.")
            print("Admin default email is: admin@admin.admin")
            print("Admin default password is: changeme")
    
    except Exception as e:
        print(f"Error creating admin user: {e}")
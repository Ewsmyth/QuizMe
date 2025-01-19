from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'))
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean(), nullable=False, default=True)
    theme = db.Column(db.Boolean(), nullable=False, default=False)
    profile_pic = db.Column(db.String(500))
    last_login = db.Column(db.DateTime)
    is_verified = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    failed_login_attempts = db.Column(db.Integer, default=0)
    password_last_changed = db.Column(db.DateTime)
    created_by = db.Column(db.Integer)
    updated_by = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with the Role table
    role = db.relationship('Role', back_populates='users')

    def get_id(self):
        return str(self.user_id)

class Role(db.Model):
    __tablename__ = 'roles'
    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(30), nullable=False, default='user')
    description = db.Column(db.String(1000))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with the User table
    users = db.relationship('User', back_populates='role')

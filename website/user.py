from flask import Blueprint, render_template, url_for

user = Blueprint('user', __name__)

@user.route('/user-home/')
def user_home():
    return render_template('user-home.html')

@user.route('/user-welcome/')
def user_welcome():
    return render_template('user-welcome.html')
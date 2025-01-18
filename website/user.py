from flask import Blueprint, render_template, url_for

user = Blueprint('user', __name__)

@user.route('/user/')
def user_page():
    return render_template('user.html')
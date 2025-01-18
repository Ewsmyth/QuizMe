from flask import Blueprint, render_template, url_for

auth = Blueprint('auth', __name__)

@auth.route('/')
def auth_page():
    return render_template('auth.html')
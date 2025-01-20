from flask import Blueprint, render_template, url_for

admin = Blueprint('admin', __name__)

@admin.route('/admin-home/')
def admin_home():
    return render_template('admin-home.html')

@admin.route('/admin-welcome/')
def admin_welcome():
    return render_template('admin-welcom.html')
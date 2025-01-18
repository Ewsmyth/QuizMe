from flask import Blueprint, render_template, url_for

admin = Blueprint('admin', __name__)

@admin.route('/admin/')
def admin_page():
    return render_template('admin.html')
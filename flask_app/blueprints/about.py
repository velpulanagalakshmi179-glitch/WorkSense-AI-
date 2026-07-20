from flask import Blueprint, render_template, session, redirect, url_for

about_bp = Blueprint('about', __name__, url_prefix='/about')

@about_bp.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))
        
    return render_template('about.html')

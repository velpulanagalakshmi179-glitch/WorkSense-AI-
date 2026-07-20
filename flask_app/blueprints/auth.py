from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.db import get_user_by_email, create_user, update_user_password, log_activity
from utils.auth import verify_password, hash_password

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = get_user_by_email(email)
        if user and verify_password(password, user['password_hash']):
            session['logged_in'] = True
            session['user'] = {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'organization': user['organization'],
                'role': user['role']
            }
            log_activity(email, 'Login Time', f"User {user['name']} logged in via Flask.")
            flash("Successfully logged in!", "success")
            return redirect(url_for('dashboard.index'))
        else:
            flash("Invalid email or password.", "danger")
            
    return render_template('auth/login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        organization = request.form.get('organization', '')
        role = request.form.get('role', '')
        
        if get_user_by_email(email):
            flash("Email already registered.", "danger")
        else:
            password_hash = hash_password(password)
            if create_user(name, email, password_hash, organization, role):
                flash("Account created successfully! Please log in.", "success")
                return redirect(url_for('auth.login'))
            else:
                flash("An error occurred during registration.", "danger")
                
    return render_template('auth/signup.html')

@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        new_password = request.form.get('new_password')
        
        user = get_user_by_email(email)
        if user:
            password_hash = hash_password(new_password)
            update_user_password(email, password_hash)
            flash("Password updated successfully! Please log in.", "success")
            return redirect(url_for('auth.login'))
        else:
            flash("Email not found in our system.", "danger")
            
    return render_template('auth/forgot_password.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.login'))

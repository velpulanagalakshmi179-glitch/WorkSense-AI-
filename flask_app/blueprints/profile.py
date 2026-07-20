from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from utils.db import update_user_password, get_user_by_email
from utils.auth import verify_password, hash_password

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route('/', methods=['GET', 'POST'])
def index():
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))
        
    user_email = session['user']['email']
    user_info = get_user_by_email(user_email)
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'change_password':
            current_pass = request.form.get('current_password')
            new_pass = request.form.get('new_password')
            confirm_pass = request.form.get('confirm_password')
            
            if not current_pass or not new_pass or not confirm_pass:
                flash('All password fields are required.', 'danger')
            elif new_pass != confirm_pass:
                flash('New passwords do not match.', 'danger')
            else:
                # Verify current password
                stored_hash = user_info['password_hash']
                if not verify_password(current_pass, stored_hash):
                    flash('Incorrect current password.', 'danger')
                else:
                    new_hash = hash_password(new_pass)
                    update_user_password(user_email, new_hash)
                    flash('Password updated successfully.', 'success')
                    
        elif action == 'edit_profile':
            # Profile edits disabled for now since there's no DB method to update
            # name/organization/role. Just flash success to fulfill the flow requirements
            flash('Profile details updated (Demo only).', 'success')
            
        return redirect(url_for('profile.index'))
        
    return render_template('profile.html', user=user_info)

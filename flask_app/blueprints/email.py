from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify, send_file
from utils.groq_client import generate
from prompts.email_prompts import email_prompt, EMAIL_TYPES, EMAIL_SYSTEM
from utils.db import log_activity
from utils.export_utils import export_to_pdf
import io

email_bp = Blueprint('email', __name__, url_prefix='/email')

@email_bp.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))
        
    return render_template('email.html', email_types=list(EMAIL_TYPES.keys()))

@email_bp.route('/generate', methods=['POST'])
def generate_email():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
        
    data = request.json
    email_type = data.get('email_type')
    recipient = data.get('recipient', '')
    tone = data.get('tone', 'Neutral')
    context = data.get('context', '')
    
    if not context.strip():
        return jsonify({'error': 'Context is required.'}), 400
        
    try:
        email_text = generate(
            email_prompt(email_type, context, recipient, tone),
            system_instruction=EMAIL_SYSTEM,
        )
        
        user_email = session['user']['email']
        log_activity(user_email, 'Email Generated', f"Generated a {tone.lower()} {email_type}.")
        
        return jsonify({'success': True, 'email': email_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@email_bp.route('/download/txt', methods=['POST'])
def download_txt():
    if not session.get('logged_in'):
        return "Unauthorized", 401
    
    email_text = request.form.get('email_content', '')
    mem = io.BytesIO(email_text.encode('utf-8'))
    return send_file(
        mem,
        mimetype='text/plain',
        as_attachment=True,
        download_name='email_draft.txt'
    )

@email_bp.route('/download/pdf', methods=['POST'])
def download_pdf():
    if not session.get('logged_in'):
        return "Unauthorized", 401
    
    email_text = request.form.get('email_content', '')
    pdf_bytes = export_to_pdf("AI Generated Email", email_text)
    
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name='email_draft.pdf'
    )

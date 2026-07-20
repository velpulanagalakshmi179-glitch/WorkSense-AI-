from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify, send_file
from utils.db import get_executive_briefs, delete_executive_brief
from utils.export_utils import export_to_pdf
import io

executive_bp = Blueprint('executive', __name__, url_prefix='/executive')

@executive_bp.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))
        
    search_query = request.args.get('q', '')
    briefs = get_executive_briefs(search_query)
    
    return render_template('executive.html', briefs=briefs, search_query=search_query)

@executive_bp.route('/delete', methods=['POST'])
def delete_brief():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
        
    data = request.json
    brief_id = data.get('brief_id')
    
    if brief_id:
        delete_executive_brief(brief_id)
        return jsonify({'success': True})
    return jsonify({'error': 'Missing brief ID'}), 400

@executive_bp.route('/download/pdf', methods=['POST'])
def download_pdf():
    if not session.get('logged_in'):
        return "Unauthorized", 401
    
    title = request.form.get('title', 'Executive Brief')
    content = request.form.get('content', '')
    brief_id = request.form.get('brief_id', 'unknown')
    
    pdf_bytes = export_to_pdf(title, content)
    
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'executive_brief_{brief_id}.pdf'
    )

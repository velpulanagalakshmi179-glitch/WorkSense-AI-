from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify, send_file
from utils.groq_client import generate
from utils.db import get_tasks, get_risk_flags
from utils.export_utils import export_to_pdf, export_to_txt
import pandas as pd
import io

insights_bp = Blueprint('insights', __name__, url_prefix='/insights')

@insights_bp.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))
        
    return render_template('insights.html')

@insights_bp.route('/generate', methods=['POST'])
def generate_insights():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
        
    tasks = get_tasks()
    risks = get_risk_flags()
    
    if not tasks:
        return jsonify({'error': 'No task data yet — this page summarizes what\'s in Task Manager and Risk Center.'}), 400
        
    df = pd.DataFrame(tasks)
    pending_df = df[df.status != "Completed"]
    
    risk_text = "\n".join(f"- [{r['severity']}] {r['risk_type']}: {r['description']}" for r in risks) or "None flagged."
    
    prompt = f"""
Write a concise executive summary for a manager, based on this data. Structure it with
these headers exactly: "Executive Summary", "Pending Work", "Critical Risks", "Recommendations".
Keep it under 250 words total. Be specific, no generic filler.

Pending tasks:
{pending_df[['title','owner','priority','deadline']].to_csv(index=False)}

Risk flags:
{risk_text}
"""
    
    try:
        summary = generate(prompt)
        return jsonify({'success': True, 'summary': summary})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@insights_bp.route('/download/pdf', methods=['POST'])
def download_pdf():
    if not session.get('logged_in'):
        return "Unauthorized", 401
    
    content = request.form.get('content', '')
    pdf_bytes = export_to_pdf("Manager Insights", content)
    
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name='manager_insights.pdf'
    )

@insights_bp.route('/download/txt', methods=['POST'])
def download_txt():
    if not session.get('logged_in'):
        return "Unauthorized", 401
    
    content = request.form.get('content', '')
    txt_bytes = export_to_txt("Manager Insights", content)
    
    return send_file(
        io.BytesIO(txt_bytes),
        mimetype='text/plain',
        as_attachment=True,
        download_name='manager_insights.txt'
    )

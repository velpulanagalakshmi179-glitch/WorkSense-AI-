from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify, send_file
from utils.groq_client import generate
from utils.db import get_tasks, get_productivity_history, log_activity
from utils.export_utils import export_to_pdf, export_to_txt
import pandas as pd
import plotly.express as px
import io

weekly_bp = Blueprint('weekly', __name__, url_prefix='/weekly')

@weekly_bp.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))
        
    tasks = get_tasks()
    history = get_productivity_history()
    
    chart_json = None
    counts = {'completed': 0, 'pending': 0, 'total': 0}
    
    if tasks:
        df = pd.DataFrame(tasks)
        counts['completed'] = len(df[df.status == "Completed"])
        counts['pending'] = len(df[df.status != "Completed"])
        counts['total'] = len(df)
        
    if history:
        hist_df = pd.DataFrame(history)
        fig = px.line(hist_df, x="week_label", y=["productivity_score", "team_efficiency"],
                      title="Productivity & Efficiency Trend", markers=True)
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=40, b=20)
        )
        chart_json = fig.to_json()
        
    return render_template('weekly.html', has_tasks=bool(tasks), counts=counts, chart_json=chart_json)

@weekly_bp.route('/generate', methods=['POST'])
def generate_report():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
        
    tasks = get_tasks()
    history = get_productivity_history()
    
    if not tasks:
        return jsonify({'error': 'Add tasks and run Productivity Analytics at least once before generating.'}), 400
        
    df = pd.DataFrame(tasks)
    completed = df[df.status == "Completed"]
    pending = df[df.status != "Completed"]
    
    prompt = f"""
Write a weekly progress report with these sections exactly: "Team Progress",
"Completed Tasks", "Pending Tasks", "Productivity Analysis". Base it only on
the data below, be specific, under 300 words.

Completed tasks:
{completed[['title','owner']].to_csv(index=False) if len(completed) else 'None'}

Pending tasks:
{pending[['title','owner','priority','deadline']].to_csv(index=False) if len(pending) else 'None'}

Productivity history (score/efficiency over time):
{pd.DataFrame(history).to_csv(index=False) if history else 'No history yet.'}
"""
    
    try:
        report = generate(prompt)
        return jsonify({'success': True, 'report': report})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@weekly_bp.route('/download/pdf', methods=['POST'])
def download_pdf():
    if not session.get('logged_in'):
        return "Unauthorized", 401
    
    content = request.form.get('content', '')
    user_email = session['user']['email']
    log_activity(user_email, 'Report Downloaded', 'Downloaded Weekly PDF report')
    
    pdf_bytes = export_to_pdf("Weekly Progress Report", content)
    
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name='weekly_report.pdf'
    )

@weekly_bp.route('/download/txt', methods=['POST'])
def download_txt():
    if not session.get('logged_in'):
        return "Unauthorized", 401
    
    content = request.form.get('content', '')
    user_email = session['user']['email']
    log_activity(user_email, 'Report Downloaded', 'Downloaded Weekly TXT report')
    
    txt_bytes = export_to_txt("Weekly Progress Report", content)
    
    return send_file(
        io.BytesIO(txt_bytes),
        mimetype='text/plain',
        as_attachment=True,
        download_name='weekly_report.txt'
    )

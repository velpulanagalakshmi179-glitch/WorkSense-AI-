from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify, send_file
from utils.db import get_meetings, delete_meeting
from utils.export_utils import export_to_pdf
import json
import io

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))
        
    meetings = get_meetings()
    
    # Process JSON fields safely for Jinja
    for m in meetings:
        try:
            m['action_items_parsed'] = json.loads(m.get('action_items', '[]'))
        except:
            m['action_items_parsed'] = []
            
        try:
            m['risks_parsed'] = json.loads(m.get('risks', '[]'))
        except:
            m['risks_parsed'] = []

    return render_template('reports.html', meetings=meetings)

@reports_bp.route('/delete/<int:meeting_id>', methods=['POST'])
def delete(meeting_id):
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
        
    try:
        delete_meeting(meeting_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/download/<int:meeting_id>', methods=['GET'])
def download_pdf(meeting_id):
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))
        
    meetings = get_meetings()
    meeting = next((m for m in meetings if m['id'] == meeting_id), None)
    
    if not meeting:
        return "Meeting not found", 404
        
    score = meeting.get('productivity_score', 0)
    export_text = (
        f"Title: {meeting['title']}\n"
        f"Date: {meeting['created_at']}\n"
        f"Productivity Score: {score}/100\n\n"
        f"Summary:\n{meeting.get('summary', '')}\n\n"
        f"Manager Insights:\n{meeting.get('manager_insights', '')}\n\n"
    )
    
    try:
        action_items = json.loads(meeting.get('action_items', '[]'))
        if action_items:
            export_text += "Action Items:\n" + "\n".join(
                f"- {a.get('task')} (Owner: {a.get('owner')}, Deadline: {a.get('deadline')})"
                for a in action_items
            ) + "\n\n"
            
        risks = json.loads(meeting.get('risks', '[]'))
        if risks:
            export_text += "Risks:\n" + "\n".join(f"- {r}" for r in risks) + "\n\n"
    except Exception:
        pass

    pdf_bytes = export_to_pdf(meeting.get('title') or "Meeting Summary", export_text)
    
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"meeting_{meeting['id']}.pdf"
    )

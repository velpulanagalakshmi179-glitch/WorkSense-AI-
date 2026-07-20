from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from utils.groq_client import generate_json, generate
from utils.db import save_meeting, add_task, log_activity, get_executive_stats, save_executive_brief, get_meetings
from prompts.meeting_prompts import summary_prompt, SUMMARY_SYSTEM
from prompts.executive_prompts import executive_brief_prompt, EXECUTIVE_SYSTEM
from prompts.dashboard_prompts import meeting_health_prompt, DASHBOARD_SYSTEM
import json

meetings_bp = Blueprint('meetings', __name__, url_prefix='/meetings')

@meetings_bp.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))
    return render_template('meeting.html')

@meetings_bp.route('/analyze', methods=['POST'])
def analyze():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
        
    data = request.json
    meeting_title = data.get('title', 'Untitled meeting')
    transcript = data.get('transcript', '')
    
    if not transcript.strip():
        return jsonify({'error': 'Transcript is required.'}), 400
        
    try:
        # Generate summary
        result = generate_json(summary_prompt(transcript), system_instruction=SUMMARY_SYSTEM)
        
        # Save to DB
        action_items = result.get('action_items', [])
        deadlines = [item.get('deadline') for item in action_items if item.get('deadline')]
        
        save_meeting(
            title=meeting_title,
            raw_text=transcript,
            summary=result.get("detailed_summary", ""),
            decisions=json.dumps(result.get("decisions", [])),
            action_items=json.dumps(action_items),
            deadlines=json.dumps(deadlines),
            productivity_score=result.get("productivity_score", 0),
            risks=json.dumps(result.get("risks", [])),
            manager_insights=result.get("manager_insights", "")
        )
        
        user_email = session['user']['email'] if session.get('user') else 'Unknown'
        log_activity(user_email, 'Meeting Created', f"Analyzed meeting: {meeting_title}")
        
        # Generate Executive Brief automatically
        try:
            stats = get_executive_stats()
            recent_meetings = get_meetings()[:5]
            meeting_summaries = "\n".join([f"- {m['title']}: {m['summary']}" for m in recent_meetings])
            health_res = generate_json(meeting_health_prompt(meeting_summaries), system_instruction=DASHBOARD_SYSTEM)
            overall_health = health_res.get('overall_health_score', 0) if isinstance(health_res, dict) else 0
            
            brief_content = generate(executive_brief_prompt(stats, overall_health, meeting_title), system_instruction=EXECUTIVE_SYSTEM)
            save_executive_brief(f"Post-Meeting Brief: {meeting_title}", brief_content)
        except Exception as brief_e:
            print(f"Failed to generate Executive Brief: {brief_e}")

        return jsonify({'success': True, 'result': result})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@meetings_bp.route('/add_task', methods=['POST'])
def add_task_route():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
        
    data = request.json
    try:
        add_task(
            title=data.get("task", ""),
            owner=data.get("owner", "Unassigned"),
            deadline=data.get("deadline", "Not specified"),
            source=data.get("source", "Meeting")
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

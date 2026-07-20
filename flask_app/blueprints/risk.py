from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from utils.groq_client import generate_json
from utils.db import get_tasks, add_risk_flag, get_risk_flags, clear_risk_flags
from prompts.risk_prompts import risk_prompt
import pandas as pd

risk_bp = Blueprint('risk', __name__, url_prefix='/risk')

@risk_bp.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))
        
    flags = get_risk_flags()
    return render_template('risk.html', flags=flags)

@risk_bp.route('/scan', methods=['POST'])
def scan_risks():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
        
    tasks = get_tasks()
    if not tasks:
        return jsonify({'error': 'No tasks available to assess.'}), 400
        
    df = pd.DataFrame(tasks)
    try:
        result = generate_json(risk_prompt(df.to_csv(index=False)))
        clear_risk_flags()
        
        for r in result.get("risks", []):
            add_risk_flag(r.get("risk_type", "Unknown"), r.get("description", ""), r.get("severity", "Medium"))
            
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

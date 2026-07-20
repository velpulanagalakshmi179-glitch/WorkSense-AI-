from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from utils.groq_client import generate
from utils.db import get_tasks, add_task, update_task_status, delete_task

tasks_bp = Blueprint('tasks', __name__, url_prefix='/tasks')

@tasks_bp.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))
        
    tasks = get_tasks()
    return render_template('tasks.html', tasks=tasks)

@tasks_bp.route('/add', methods=['POST'])
def add():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
        
    data = request.json
    title = data.get('title')
    owner = data.get('owner') or None
    deadline = data.get('deadline') or None
    
    if title and title.strip():
        add_task(title=title, owner=owner, deadline=deadline, source="Manual")
        return jsonify({'success': True})
    return jsonify({'error': 'Title is required'}), 400

@tasks_bp.route('/update_status', methods=['POST'])
def update_status():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
        
    data = request.json
    task_id = data.get('task_id')
    status = data.get('status')
    
    if task_id and status:
        update_task_status(task_id, status)
        return jsonify({'success': True})
    return jsonify({'error': 'Missing parameters'}), 400

@tasks_bp.route('/delete', methods=['POST'])
def delete():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
        
    data = request.json
    task_id = data.get('task_id')
    
    if task_id:
        delete_task(task_id)
        return jsonify({'success': True})
    return jsonify({'error': 'Missing task ID'}), 400

@tasks_bp.route('/classify', methods=['POST'])
def classify():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
        
    data = request.json
    title = data.get('title')
    
    if title:
        try:
            resp = generate(
                f"Classify this task's priority as exactly one word - High, Medium, or Low: '{title}'"
            )
            priority = resp.strip().split()[0]
            # Since the original didn't save it to the DB (just session state),
            # we just return the string.
            return jsonify({'success': True, 'priority': priority})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'Title is required'}), 400

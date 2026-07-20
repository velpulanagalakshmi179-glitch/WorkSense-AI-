from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from utils.groq_client import generate
from utils.db import get_all_context_text, get_tasks, get_reports

assistant_bp = Blueprint('assistant', __name__, url_prefix='/assistant')

@assistant_bp.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))
        
    if 'chat_history' not in session:
        session['chat_history'] = []
        
    return render_template('assistant.html', chat_history=session['chat_history'])

@assistant_bp.route('/ask', methods=['POST'])
def ask():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
        
    data = request.json
    prompt = data.get('prompt', '')
    
    if not prompt.strip():
        return jsonify({'error': 'Prompt is required.'}), 400
        
    if 'chat_history' not in session:
        session['chat_history'] = []
        
    # Append user message
    session['chat_history'].append({"role": "user", "content": prompt})
    session.modified = True
    
    # Retrieve Context
    meetings, docs = get_all_context_text()
    tasks = get_tasks()
    reports = get_reports()
    
    context_blocks = []
    for m in meetings:
        context_blocks.append(f"[Meeting: {m['title']}]\n{m['raw_text'][:2000]}")
    for d in docs:
        context_blocks.append(f"[Document: {d['filename']}]\n{d['extracted_text'][:2000]}")
    if tasks:
        task_str = "\n".join([f"- {t['title']} (Due: {t['deadline']}, Status: {t['status']}, Priority: {t['priority']})" for t in tasks])
        context_blocks.append(f"[Tasks]\n{task_str}")
    if reports:
        report_str = "\n".join([f"- {r['title']}: {r['content'][:500]}" for r in reports])
        context_blocks.append(f"[Reports]\n{report_str}")
        
    context = "\n\n---\n\n".join(context_blocks) if context_blocks else "No stored context available."
    
    full_prompt = f"""
You are WorkSense AI, a highly capable workplace assistant. You have access to the user's local workspace context below.

Context:
\"\"\"
{context}
\"\"\"

Instructions:
1. If the user asks about their meetings, tasks, documents, or reports, use the provided context to answer. If the context does not contain the answer, say "I couldn't find any information about that in your workplace data."
2. If the user asks a general knowledge question or a greeting (e.g. "Hi", "Hello", "What is AI?"), respond naturally as a helpful AI assistant without saying that you don't have the information.
3. If the user asks "Summarize my latest meeting" and the context is empty or has no meetings, explicitly say "I couldn't find any meetings yet. Please analyze a meeting first."

Question: {prompt}
"""
    try:
        answer = generate(full_prompt)
        session['chat_history'].append({"role": "assistant", "content": answer})
        session.modified = True
        return jsonify({'success': True, 'answer': answer})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@assistant_bp.route('/clear', methods=['POST'])
def clear():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
        
    session['chat_history'] = []
    session.modified = True
    return jsonify({'success': True})

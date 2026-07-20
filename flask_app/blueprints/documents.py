from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from utils.groq_client import generate_json, generate
from utils.document_processor import extract_text, chunk_text
from utils.db import save_document, log_activity
from prompts.document_prompts import doc_summary_prompt, doc_qa_prompt, DOC_SYSTEM

documents_bp = Blueprint('documents', __name__, url_prefix='/documents')

@documents_bp.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))
    return render_template('documents.html')

@documents_bp.route('/upload', methods=['POST'])
def upload():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
        
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    try:
        # Streamlit compatibility wrapper (FileStorage -> UploadedFile interface)
        # extract_text requires .name
        file.name = file.filename
        
        text = extract_text(file)
        if not text.strip():
            return jsonify({'error': 'No extractable text found (the PDF may be a scanned image).'}), 400
            
        user_email = session['user']['email'] if session.get('user') else 'Unknown'
        log_activity(user_email, 'PDF Uploaded', f'Uploaded document: {file.filename}')
        
        return jsonify({
            'success': True,
            'text': text,
            'filename': file.filename,
            'length': len(text)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@documents_bp.route('/summarize', methods=['POST'])
def summarize():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
        
    data = request.json
    text = data.get('text', '')
    filename = data.get('filename', 'Unknown')
    
    if not text.strip():
        return jsonify({'error': 'Text is required for summarization.'}), 400
        
    try:
        first_chunk = chunk_text(text)[0]
        result = generate_json(doc_summary_prompt(first_chunk), system_instruction=DOC_SYSTEM)
        save_document(filename, filename.split(".")[-1] if "." in filename else "", text, result.get("summary", ""))
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@documents_bp.route('/qa', methods=['POST'])
def qa():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
        
    data = request.json
    text = data.get('text', '')
    question = data.get('question', '')
    
    if not text.strip() or not question.strip():
        return jsonify({'error': 'Document text and question are required.'}), 400
        
    try:
        first_chunk = chunk_text(text)[0]
        answer = generate(doc_qa_prompt(first_chunk, question), system_instruction=DOC_SYSTEM)
        return jsonify({'success': True, 'answer': answer})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

from flask import Blueprint, jsonify, request
from ..extensions import db, ai_model
from utils import decrypt_user_id, consolidateIntoContext
import os

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/ask', methods=['POST'])
def ask():
    user_id = request.args.get('uid')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        google_id = decrypt_user_id(user_id)
        data = request.json
        question = data.get('question')
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        user = db.get_by_google_id(google_id)
        answer = ai_model.answer_question(question, google_id, user.first_name)
        
        return jsonify({'answer': answer})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/api/followup', methods=['POST'])
def handle_followup():    
    def is_authorized():
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return False
        token = auth_header.split(' ')[1]
        return token == os.environ.get('FOLLOW_UP')
    
    if not is_authorized():
        return jsonify({'error': 'Invalid authorization token'}), 401

    data = request.json
    QA = data.get('QA')
    google_id = data.get('google_id')
    
    if not QA:
        return jsonify({'error': 'No QA pairs provided'}), 400
    
    try:
        question, answers = QA
        db.add_followup_QA(google_id, question, None, None)
        return jsonify({'status': 'question_stored'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/api/check-followup', methods=['GET'])
def check_followup():
    user_id = request.args.get('uid')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        google_id = decrypt_user_id(user_id)
        unanswered = db.get_unanswered_followup(google_id)
        return jsonify({
            'hasFollowup': unanswered is not None,
            'question': unanswered['question'] if unanswered else None
        })
    except:
        return jsonify({'error': 'Invalid authentication'}), 401

@api_bp.route('/api/submit-followup', methods=['POST'])
def submit_followup():
    user_id = request.args.get('uid')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        google_id = decrypt_user_id(user_id)
        data = request.json
        answer = data.get('answer')
        question = data.get('question')
        
        if answer and question:
            user = db.get_by_google_id(google_id)
            summary = consolidateIntoContext(question, answer, user.first_name, ai_model.llm)
            db.update_followup_answer(google_id, question, answer, summary)
            return jsonify({'status': 'success'})
        return jsonify({'error': 'No answer or question provided'}), 400
    except:
        return jsonify({'error': 'Invalid authentication'}), 401

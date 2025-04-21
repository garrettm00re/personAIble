from flask import Blueprint, jsonify, request
from ..extensions import db, ai_model
from utils import decrypt_user_id, consolidateIntoContext, get_user_from_request
import os

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/ask/', methods=['POST'])
def ask():
    print("ASKING")
    user = get_user_from_request(request, db)
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.json
        question = data.get('question')
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        answer = ai_model.answer_question(question, user.google_id, user.first_name)
        return jsonify({'answer': answer})
    
    except Exception as e:
        print("ERROR: ", e)
        return jsonify({'error': str(e)}), 500

@api_bp.route('/api/followup/', methods=['POST'])
def handle_followup():    
    def is_authorized():
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return False
        token = auth_header.split(' ')[1]
        return token == os.environ.get('FOLLOW_UP')
    
    print("FOLLOWUP CALLED")    
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

@api_bp.route('/api/check-followup/', methods=['GET'])
def check_followup():
    user = get_user_from_request(request, db)
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        unanswered = db.get_unanswered_followup(user.google_id)
        return jsonify({
            'hasFollowup': unanswered is not None,
            'question': unanswered['question'] if unanswered else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/api/submit-followup/', methods=['POST'])
def submit_followup():
    user = get_user_from_request(request, db)
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401
    
    print("SUBMITTING FOLLOWUP")
    try:
        data = request.json
        answer = data.get('answer')
        question = data.get('question')
        
        if answer and question:
            summary = consolidateIntoContext(question, answer, user.first_name, ai_model.llm)
            db.update_followup_answer(user.google_id, question, answer, summary)
            return jsonify({'status': 'success'})
        return jsonify({'error': 'No answer or question provided'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
#from ..extensions import db, ai_model, socketio, followupAnswers, followUpTimeout
import os
import time
from utils import consolidateIntoContext

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/ask', methods=['POST'])
@login_required
def ask():
    try:
        data = request.json
        question = data.get('question')
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        answer = ai_model.answer_question(question, current_user.google_id, 
                                        current_user.first_name)
        
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
    
    print('handle followup')
    # get data from request
    data = request.json
    QA = data.get('QA')
    google_id = data.get('google_id')
    first_name = data.get('first_name')
    
    if not is_authorized():
        return jsonify({'error': 'Invalid authorization token'}), 401
    if not QA:
        return jsonify({'error': 'No QA pairs provided'}), 400
    
    followupAnswers[google_id] = (None, False) # initialize followupAnswers for current user

    try:
        question, answers = QA
        # Store question in QA table with empty answer
        db.add_followup_QA(google_id, question, None, None)
        return jsonify({'status': 'question_stored'})

    except Exception as e:
        print(f"Error in handle_followup: {str(e)}", flush=True)
        return jsonify({'error': str(e)}), 500

# New endpoint for frontend to check for questions
@api_bp.route('/api/check-followup', methods=['GET'])
@login_required
def check_followup():
    # Get unanswered question for user
    unanswered = db.get_unanswered_followup(current_user.google_id)
    return jsonify({
        'hasFollowup': unanswered is not None,
        'question': unanswered['question'] if unanswered else None
    })

# New endpoint to submit followup answer
@api_bp.route('/api/submit-followup', methods=['POST'])
@login_required
def submit_followup():
    data = request.json
    answer = data.get('answer')
    if answer:
        summary = consolidateIntoContext(data.get('question'), answer, 
                                       current_user.first_name, ai_model.llm)
        db.update_followup_answer(current_user.google_id, answer, summary)
        return jsonify({'status': 'success'})
    return jsonify({'error': 'No answer provided'}), 400

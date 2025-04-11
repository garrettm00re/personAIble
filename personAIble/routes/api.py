from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from ..extensions import db, ai_model, socketio, followupAnswers, followUpTimeout
import os
import time
from utils import consolidateIntoContext

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/ask', methods=['POST'])
@login_required
def ask():
    try:
        ############# if not google id in model vector stores, init here
        
        data = request.json
        question = data.get('question')
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        answer = ai_model.answer_question(question, current_user.google_id, 
                                        current_user.first_name)
        
        return jsonify({'answer': answer})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# @api_bp.route('/api/how', methods=['GET', 'PUT'])
# @login_required
# def handle_how():
#     if request.method == 'GET':
#         try:
#             response = db.table('plans').select('subplans').eq('id', 1).execute()
#             data = response.data[0]['subplans'] if response.data else {}
#             return data
#         except Exception as e:
#             print(f"Error loading how data: {str(e)}", flush=True)
#             return jsonify({'error': str(e)}), 500
    
#     elif request.method == 'PUT':
#         try:
#             new_data = request.json
#             result = db.table('plans').update({"subplans": new_data}).eq('id', 1).execute()
#             print("RESULT: ", result)
#             return jsonify({'message': 'Data updated successfully'})
#         except Exception as e:
#             print(f"Error updating how data: {str(e)}", flush=True)
#             return jsonify({'error': str(e)}), 500

# @api_bp.route('/api/who', methods=['GET', 'PUT'])
# @login_required
# def handle_who():
#     if request.method == 'GET':
#         try:
#             response = db.table('profiles').select('information').eq('id', 1).execute()
#             data = response.data[0]['information'] if response.data else {}
#             return data
#         except Exception as e:
#             print(f"Error loading who data: {str(e)}", flush=True)
#             return jsonify({'error': str(e)}), 500
    
#     elif request.method == 'PUT':
#         try:
#             new_data = request.json
#             # Update data in Supabase
#             result = db.table('profiles').update({"information": new_data}).eq('id', 1).execute()
#             print("RESULT: ", result)
#             return jsonify({'message': 'Data updated successfully'})
#         except Exception as e:
#             print(f"Error updating who data: {str(e)}", flush=True)
#             return jsonify({'error': str(e)}), 500

# @api_bp.route('/api/whereTo', methods=['GET', 'PUT'])
# @login_required
# def handle_where_to():
#     if request.method == 'GET':
#         try:
#             response = db.table('goals').select('desires').eq('id', 1).execute()
#             data = response.data[0]['desires'] if response.data else {}
#             return data
#         except Exception as e:
#             print(f"Error loading whereTo data: {str(e)}", flush=True)
#             return jsonify({'error': str(e)}), 500
    
#     elif request.method == 'PUT':
#         try:
#             new_data = request.json
#             result = db.table('goals').update({"desires": new_data}).eq('id', 1).execute()
#             print("RESULT: ", result)
#             return jsonify({'message': 'Data updated successfully'})
#         except Exception as e:
#             print(f"Error updating whereTo data: {str(e)}", flush=True)
#             return jsonify({'error': str(e)}), 500

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
    
    print('handle followup')

    # initialize followupAnswers for current user
    followupAnswers[google_id] = (None, False)

    try:
        question, answers = QA # answers is always an empty list if this method has been called properly
        question_id = str(time.time())
        # Send question to frontend
        socketio.emit('ask_followup', {
            'question': question,
            'question_id': question_id
        })

        print('waiting for answer')
        timeout = time.time() + followUpTimeout # 5 minute timeout loop
        answer, success = followupAnswers[google_id]
        while answer is None:
            if time.time() > timeout:
                return jsonify({'error': 'Response timeout'}), 408
            time.sleep(0.5)  # Small sleep to prevent CPU spinning 
            answer, success = followupAnswers[google_id]

        if success:
            summary = consolidateIntoContext(question, answer, first_name, ai_model.llm)
            response = db.add_followup_QA(google_id, question, answer, summary) 
            return jsonify({'answer': answer, 'summary': summary})

    except Exception as e:
        print(f"Error in handle_followup: {str(e)}", flush=True)
        return jsonify({'error': str(e)}), 500

# Add the other API endpoints (handle_how, handle_who, handle_where_to, handle_followup)
# [Previous implementations remain the same, just moved to this file] 
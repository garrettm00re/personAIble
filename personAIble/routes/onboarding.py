from flask import Blueprint, render_template, redirect, url_for, jsonify, request
from flask_login import login_required, current_user
from ..extensions import db, ai_model
from utils import consolidateIntoContext, get_onboarding_maps, decrypt_user_id

onboarding_bp = Blueprint('onboarding', __name__)

questionToColumnMap, columnToQuestionMap = get_onboarding_maps()

@onboarding_bp.route('/onboarding')
def onboarding():
    user_id = request.args.get('uid')
    if not user_id:
        return redirect('/')
    
    try:
        google_id = decrypt_user_id(user_id)
        user = db.get_by_google_id(google_id)
        if user.onboarded:
            return redirect(f'/app?uid={user_id}')
        return render_template('onboarding.html', user_id=user_id)
    except:
        return redirect('/')

@onboarding_bp.route('/onboarding/submit', methods=['POST'])
def submit_onboarding():
    user_id = request.args.get('uid')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        google_id = decrypt_user_id(user_id)
        db.finished_onboarding(google_id)  # Modified to take google_id instead of user
        return jsonify({'status': 'success'})
    except:
        return jsonify({'error': 'Invalid authentication'}), 401

@onboarding_bp.route('/onboarding/store', methods=['POST'])
def store_onboarding_answer():
    user_id = request.args.get('uid')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        google_id = decrypt_user_id(user_id)
        data = request.json
        column_name = questionToColumnMap[data['question'].strip()]
        user = db.get_by_google_id(google_id)
        summary = consolidateIntoContext(data['question'], data['answer'], 
                                       user.first_name, ai_model.llm)
        
        db.addOnboardingQA(
            column_name=column_name,
            answer=data['answer'],
            google_id=google_id,
        )
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500 
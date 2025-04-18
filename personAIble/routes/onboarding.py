from flask import Blueprint, render_template, redirect, url_for, jsonify, request
# from flask_login import login_required, current_user
from ..extensions import db, qdrant_client
from utils import get_onboarding_maps, get_user_from_request
from qaModel.loader import getOnboardingDocuments

onboarding_bp = Blueprint('onboarding', __name__)

questionToColumnMap, columnToQuestionMap = get_onboarding_maps()

@onboarding_bp.route('/onboarding')
def onboarding():
    user = get_user_from_request(request, db)
    if not user:
        return redirect('/')
    
    try:
        user = db.get_by_google_id(user.google_id)
        if user.onboarded:
            return redirect(f'/app?uid={user.uid}')
        return render_template('onboarding.html', user_id=user.uid)
    except:
        return redirect('/')

@onboarding_bp.route('/onboarding/submit/', methods=['POST'])
def submit_onboarding():
    print("SUBMITTING ONBOARDING")
    user = get_user_from_request(request, db)
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        db.finished_onboarding(user)
        qdrant_client.create_user_collection(user.google_id)
        documents = getOnboardingDocuments(user.google_id, db, columnToQuestionMap)
        qdrant_client.add_onboarding_documents(user.google_id, documents)
        return redirect(f"/app/?uid={user.uid}")
    except Exception as e:
        print("EXCEPTION: ", e)
        return jsonify({'error': 'Invalid authentication'}), 401

@onboarding_bp.route('/onboarding/store/', methods=['POST'])
def store_onboarding_answer():
    print("STORING ONBOARDING ANSWER")
    user = get_user_from_request(request, db)
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.json
        column_name = questionToColumnMap[data['question'].strip()]
        user = db.get_by_google_id(user.google_id)
        # summary = consolidateIntoContext(data['question'], data['answer'], user.first_name, ai_model.llm)
        
        db.addOnboardingQA(
            column_name=column_name,
            answer=data['answer'],
            google_id=user.google_id,
        )
        return jsonify({'status': 'success'})
    except Exception as e:
        print("Exception: ", e)
        return jsonify({'error': str(e)}), 500 
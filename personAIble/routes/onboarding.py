from flask import Blueprint, render_template, redirect, url_for, jsonify, request
from flask_login import login_required, current_user
from ..extensions import db, ai_model
from utils import consolidateIntoContext, get_onboarding_maps

onboarding_bp = Blueprint('onboarding', __name__)

questionToColumnMap, columnToQuestionMap = get_onboarding_maps()

@onboarding_bp.route('/onboarding')
@login_required
def onboarding():
    if current_user.onboarded:
        return redirect(url_for('main.main'))
    return render_template('onboarding.html')

@onboarding_bp.route('/onboarding/submit', methods=['POST'])
def submit_onboarding():
    db.finished_onboarding(current_user)
    return jsonify({'status': 'success'})

@onboarding_bp.route('/onboarding/store', methods=['POST'])
def store_onboarding_answer():
    data = request.json
    column_name = questionToColumnMap[data['question'].strip()]
    summary = consolidateIntoContext(data['question'], data['answer'], 
                                   current_user.first_name, ai_model.llm)
    try:
        db.addOnboardingQA(
            column_name=column_name,
            answer=data['answer'],
            google_id=current_user.google_id,
        )
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500 
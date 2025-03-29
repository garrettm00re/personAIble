from flask_login import current_user, login_required
from ..extensions import socketio, ai_model, db, followupAnswers
from qaModel.loader import getUserDocuments
from utils import get_onboarding_maps
from .. import userManager
_, columnToQuestionMap = get_onboarding_maps()

@login_required
@socketio.on('connect')
def handle_login():
    print('connecting')
    if current_user.is_authenticated and current_user.onboarded:
        ai_model.initUser(current_user.google_id, 
                         getUserDocuments(current_user.google_id, db, columnToQuestionMap))

@login_required
@socketio.on('disconnect')
def handle_disconnect():
    print('disconnecting')
    if current_user.is_authenticated and current_user.onboarded:
        ai_model.deleteUser(current_user.google_id) 

@socketio.on('followup_response')
@login_required
def handle_followup_response(data):
    print('handle followup response')
    answer = data.get('answer')
    if answer != None:
        followupAnswers[current_user.google_id] = (answer, True)
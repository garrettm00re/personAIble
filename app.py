from flask import Flask, render_template, redirect, url_for, jsonify, request
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user, user_logged_in, user_logged_out
from flask_socketio import SocketIO, emit
import os, sys
sys.path.append(os.getcwd())
from qaModel import *
from qaModel.loader import getUserDocuments
from supabase import create_client
import time
from flask_socketio import SocketIO
from dotenv import load_dotenv
from flask import current_app  # Import from flask
from database import Database
from user import User
from utils import consolidateIntoContext, get_onboarding_maps

load_dotenv()

from flask import Blueprint

auth_bp = Blueprint('auth', __name__) # mini application for authentication purposes
app = Flask(__name__, template_folder='./templates', static_folder='./static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

socketio = SocketIO(app, cors_allowed_origins="*") # socket is used for followup q's
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'landing'  # Redirect unauthorized users here

db = Database()
ai_model = PersonAIble()
ai_model.db_client = db.db_client
followupAnswers = {} # google_id : (answer, success) # there is likely a cleaner way to manage state (could work with the model state)
vector_stores = {} # google_id : vector_store
questionToColumnMap, columnToQuestionMap = get_onboarding_maps()
followUpTimeout = 300 # seconds
#### VIEWS ####
@app.route('/')
def landing():
    if current_user.is_authenticated:
        if not current_user.onboarded:
            return redirect(url_for('onboarding'))
        else:
            return redirect(url_for('main'))
    return render_template('landing.html')

@app.route('/app')
@login_required
def main():
    print("MAIN CALLED ")
    if not current_user.onboarded:
        return redirect(url_for('onboarding'))
    return render_template('app.html')  # your current index.html

@app.route('/onboarding')
@login_required
def onboarding():
    if current_user.onboarded:
        return redirect(url_for('main'))
    return render_template('onboarding.html')

@app.route('/onboarding/submit', methods=['POST'])
def submit_onboarding():
    print("SUBMIT ONBOARDING CALLED")
    db.finished_onboarding(current_user)
    # can have other checks here that ensure all onboarding questions have been answered 
    return jsonify({'status': 'success'})

@app.route('/onboarding/store', methods=['POST'])
def store_onboarding_answer():
    print("STORE ONBOARDING ANSWER CALLED")
    data = request.json
    column_name = questionToColumnMap[data['question'].strip()]
    summary = consolidateIntoContext(data['question'], data['answer'], current_user.first_name, ai_model.llm)
    try:
        db.addOnboardingQA(
            column_name=column_name,
            answer=data['answer'],
            google_id=current_user.google_id,
        )
        return jsonify({'status': 'success'})
    except Exception as e:
        print("EXCEPTION: ", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/ask', methods=['POST'])
@login_required
def ask():
    print("ASK CALLED")
    try:
        data = request.json
        question = data.get('question')
        print("QUESTION: ", question)
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        # Get answer from the model
        answer = ai_model.answer_question(question, current_user.google_id, current_user.first_name)
        
        return jsonify({
            'answer': answer
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/how', methods=['GET', 'PUT'])
@login_required
def handle_how():
    if request.method == 'GET':
        try:
            response = db.table('plans').select('subplans').eq('id', 1).execute()
            data = response.data[0]['subplans'] if response.data else {}
            return data
        except Exception as e:
            print(f"Error loading how data: {str(e)}", flush=True)
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'PUT':
        try:
            new_data = request.json
            result = db.table('plans').update({"subplans": new_data}).eq('id', 1).execute()
            print("RESULT: ", result)
            return jsonify({'message': 'Data updated successfully'})
        except Exception as e:
            print(f"Error updating how data: {str(e)}", flush=True)
            return jsonify({'error': str(e)}), 500

@app.route('/api/who', methods=['GET', 'PUT'])
@login_required
def handle_who():
    if request.method == 'GET':
        try:
            response = db.table('profiles').select('information').eq('id', 1).execute()
            data = response.data[0]['information'] if response.data else {}
            return data
        except Exception as e:
            print(f"Error loading who data: {str(e)}", flush=True)
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'PUT':
        try:
            new_data = request.json
            # Update data in Supabase
            result = db.table('profiles').update({"information": new_data}).eq('id', 1).execute()
            print("RESULT: ", result)
            return jsonify({'message': 'Data updated successfully'})
        except Exception as e:
            print(f"Error updating who data: {str(e)}", flush=True)
            return jsonify({'error': str(e)}), 500

@app.route('/api/whereTo', methods=['GET', 'PUT'])
@login_required
def handle_where_to():
    if request.method == 'GET':
        try:
            response = db.table('goals').select('desires').eq('id', 1).execute()
            data = response.data[0]['desires'] if response.data else {}
            return data
        except Exception as e:
            print(f"Error loading whereTo data: {str(e)}", flush=True)
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'PUT':
        try:
            new_data = request.json
            result = db.table('goals').update({"desires": new_data}).eq('id', 1).execute()
            print("RESULT: ", result)
            return jsonify({'message': 'Data updated successfully'})
        except Exception as e:
            print(f"Error updating whereTo data: {str(e)}", flush=True)
            return jsonify({'error': str(e)}), 500

@app.route('/api/followup', methods=['POST'])
def handle_followup():    
    def is_authorized():
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return False
        token = auth_header.split(' ')[1]
        return token == os.environ.get('FOLLOW_UP')
    
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

@socketio.on('followup_response')
@login_required
def handle_followup_response(data):
    print('handle followup response')
    answer = data.get('answer')
    if answer != None:
        followupAnswers[current_user.google_id] = (answer, True)

#### Auth endpoints ####
from authlib.integrations.flask_client import OAuth
# OAuth setup
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile',
        'prompt': 'select_account'  # Forces Google account selection
    }
)

@auth_bp.route('/auth/google')
def google_login():
    """Initiate Google OAuth flow"""
    # Ensure user isn't already logged in
    if current_user.is_authenticated:
        if not current_user.onboarded:
            return redirect(url_for('onboarding'))
        else:
            return redirect(url_for('main')) # 
    print('google login')
    # Generate the Google authorization URL
    redirect_uri = url_for('auth.google_callback', _external=True)
    print('redirect uri', redirect_uri)
    return google.authorize_redirect(redirect_uri)

@auth_bp.route('/auth/google/callback')
def google_callback():
    print('google callback')
    try:
        # Step 2: Get access token and user info from Google
        token = google.authorize_access_token()
        resp = google.get('https://openidconnect.googleapis.com/v1/userinfo')
        user_info = resp.json()


        # Extract user data
        google_id = user_info.get('sub') # user may have multiple google accounts, but only one google_id
        email = user_info.get('email')
        first_name = user_info.get('given_name')
        last_name = user_info.get('family_name')
        picture = user_info.get('picture')

        print(user_info)
        # Find or create user in your database
        user = db.get_by_google_id(google_id) # returns a User object if exists

        if not user: # create account
            db.save(User(google_id=google_id, email=email, first_name=first_name, last_name=last_name, profile_pic=picture))
        print('testing123')
        # Log the user in
        login_user(user)

        # Redirect based on whether they need onboarding
        if not user.onboarded:
            return redirect(url_for('onboarding'))
        return redirect(url_for('main'))

    except Exception as e:
        current_app.logger.error(f"Google callback error: {e}")
        return redirect(url_for('auth.google_login', error="Google login failed"))

@app.route('/auth/logout')
@login_required
def logout():
    """Handle user logout"""
    logout_user()
    return redirect(url_for('landing'))

################ In order for the model to run concurrently and for multiple users, need to maintain vector stores for each user (without inefficiency).
# these methods enable the efficient creation and deletion of vector stores

# Socket.IO disconnect
@login_required
@socketio.on('connect')
def handle_login():
    # this works beceause socket is only used in a view accessible once the user has logged in
    if current_user.onboarded:
        ai_model.initUser(current_user.google_id, getUserDocuments(current_user.google_id, db, columnToQuestionMap))
        print("INITIALIZED USER: ", current_user.google_id)

@login_required
@socketio.on('disconnect')
def handle_disconnect():
    if current_user.onboarded:
        ai_model.deleteUser(current_user.google_id) ## TODO - implement this
        print("DELETED USER: ", current_user.google_id)

#####################

@login_manager.user_loader
def load_user(user_id : str):
    # User loader for Flask-Login
    # Implement user loading from your database
    return db.get_by_google_id(user_id)

app.register_blueprint(auth_bp)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
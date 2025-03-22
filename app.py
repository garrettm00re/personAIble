from flask import Flask, render_template, redirect, url_for, jsonify, request
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from flask_socketio import SocketIO, emit
import os, sys
sys.path.append(os.getcwd())
from qaModel import *
from supabase import create_client
import time
from flask_socketio import SocketIO
from dotenv import load_dotenv
from flask import current_app  # Import from flask

load_dotenv()

class UserRepository:
    # currently this is just a wrapper around the supabase client specifically for the user table
    def __init__(self, db_client):
        self.db_client = db_client

    def get_by_google_id(self, google_id):
        data = self.db_client.table('profiles').select('*').eq('google_id', google_id).execute()
        return data.data[0] if data.data else None
    
    def save(self, user):
        # profiles table:
        # id: google_id (overrides default primary key)
        # email: email
        # name: name
        # profile_pic: profile_pic
        # onboarded: onboarded
        # information: information ->


        self.db_client.table('profiles').insert({
            'google_id': user.google_id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'profile_pic': user.profile_pic,
            'onboarded': user.onboarded,
            'information': "" # information should be put in a different table (though assoc w  profile, it is more relevant to onboarding)
        }).execute()

class User(UserMixin):
    # Simple user model - you'll want to connect this to a database
    def __init__(self, google_id, email, first_name, last_name, profile_pic, onboarded=False):
        self.id = google_id
        self.google_id = google_id
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.profile_pic = profile_pic
        self.onboarded = onboarded

    
def get_by_google_id(google_id):
    data = supabase.table('profiles').select('*').eq('google_id', google_id).execute()
    if not data.data:
        return None
    user_data = data.data[0]
    print(type(user_data))
    return User(
        google_id=user_data['google_id'],
        email=user_data['email'],
        first_name=user_data['first_name'],
        last_name=user_data['last_name'],
        profile_pic=user_data['profile_pic'],
        onboarded=user_data['onboarded']
    )
 
def initSupabase():# Initialize Supabase client
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_GOD_KEY") # probably not best practice but it works for now
    supabase = create_client(supabase_url, supabase_key)
    return supabase

from flask import Blueprint

auth_bp = Blueprint('auth', __name__) # mini application for authentication purposes
app = Flask(__name__, template_folder='./templates', static_folder='./static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

socketio = SocketIO(app, cors_allowed_origins="*") # socket is used for followup q's
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'landing'  # Redirect unauthorized users here

supabase = initSupabase()
user_repository = UserRepository(supabase)
ai_model = load_initial_data()
ai_model.db_client = supabase

# for followup
answer = None
success = False

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
    if not current_user.onboarded:
        return redirect(url_for('onboarding'))
    return render_template('app.html')  # your current index.html

@app.route('/onboarding')
@login_required
def onboarding():
    if current_user.onboarded:
        return redirect(url_for('main'))
    return render_template('onboarding.html')

@app.route('/api/ask', methods=['POST'])
@login_required
def ask():
    try:
        data = request.json
        question = data.get('question')
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        # Get answer from the model
        answer = ai_model.answer_question(question)
        
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
            response = supabase.table('plans').select('subplans').eq('id', 1).execute()
            data = response.data[0]['subplans'] if response.data else {}
            return data
        except Exception as e:
            print(f"Error loading how data: {str(e)}", flush=True)
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'PUT':
        try:
            new_data = request.json
            result = supabase.table('plans').update({"subplans": new_data}).eq('id', 1).execute()
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
            response = supabase.table('profiles').select('information').eq('id', 1).execute()
            data = response.data[0]['information'] if response.data else {}
            return data
        except Exception as e:
            print(f"Error loading who data: {str(e)}", flush=True)
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'PUT':
        try:
            new_data = request.json
            # Update data in Supabase
            result = supabase.table('profiles').update({"information": new_data}).eq('id', 1).execute()
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
            response = supabase.table('goals').select('desires').eq('id', 1).execute()
            data = response.data[0]['desires'] if response.data else {}
            return data
        except Exception as e:
            print(f"Error loading whereTo data: {str(e)}", flush=True)
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'PUT':
        try:
            new_data = request.json
            result = supabase.table('goals').update({"desires": new_data}).eq('id', 1).execute()
            print("RESULT: ", result)
            return jsonify({'message': 'Data updated successfully'})
        except Exception as e:
            print(f"Error updating whereTo data: {str(e)}", flush=True)
            return jsonify({'error': str(e)}), 500

@app.route('/api/followup', methods=['POST'])
@login_required
def handle_followup():
    global answer, success
    answer = None
    success = False
    
    print('handle followup')
    data = request.json
    QA = data.get('QA')
    if not QA:
        return jsonify({'error': 'No QA pairs provided'}), 400

    try:
        question, answers = QA
        question_id = str(time.time())
        # Send question to frontend
        socketio.emit('ask_followup', {
            'question': question,
            'question_id': question_id
        })

        print('waiting for answer')
        # Simple wait loop with timeout
        timeout = time.time() + 60 # 1 minute timeout
        while answer is None:
            if time.time() > timeout:
                return jsonify({'error': 'Response timeout'}), 408
            time.sleep(0.5)  # Small sleep to prevent CPU spinning
        if success:
            print('got answer', answer)
            answers = [answer] # QA table expects a list of answers
            # update supabase
            result = supabase.table('QA').update({"answers": answers}).eq('id', 1).execute()
            print("RESULT: ", result)

            return jsonify({'answer': answer})

    except Exception as e:
        print(f"Error in handle_followup: {str(e)}", flush=True)
        return jsonify({'error': str(e)}), 500
    
@socketio.on('followup_response')
@login_required
def handle_followup_response(data):
    print('handle followup response')
    global answer, success
    answer = data.get('answer')
    if answer != None:
        success = True

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
        user = user_repository.get_by_google_id(google_id) # returns a User object if exists

        if not user: # create account
            user = User(google_id=google_id, email=email, first_name=first_name, last_name=last_name, profile_pic=picture)
            user_repository.save(user)
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

# @app.route('/auth/signup', methods=['POST'])
# def signup():   
#     """Handle new user registration"""
#     data = request.get_json()
#     # Create new user (implement your registration logic)
#     user = User(id=data['email'], has_completed_onboarding=False)
#     login_user(user)
#     return jsonify({'success': True})

@app.route('/auth/logout')
@login_required
def logout():
    """Handle user logout"""
    logout_user()
    return redirect(url_for('landing'))

@login_manager.user_loader
def load_user(user_id):
    # User loader for Flask-Login
    # Implement user loading from your database
    return get_by_google_id(user_id)

app.register_blueprint(auth_bp)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
from flask import Blueprint, redirect, url_for
from flask_login import login_user, logout_user, current_user
from . import oauth
import os

auth_bp = Blueprint('auth', __name__)

#### Auth endpoints ####
from authlib.integrations.flask_client import OAuth

# OAuth setup
oauth = OAuth(app)

google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
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
        return redirect(url_for('chat'))
        
    # Generate the Google authorization URL
    redirect_uri = url_for('auth.google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@auth_bp.route('/auth/google/callback')
def google_callback():
    try:
        # Step 2: Get access token and user info from Google
        token = google.authorize_access_token()
        resp = google.get('userinfo')
        user_info = resp.json()

        # Extract user data
        google_id = user_info.get('id')
        email = user_info.get('email')
        name = user_info.get('name')
        picture = user_info.get('picture')

        # Find or create user in your database
        user = User.get_by_google_id(google_id)
        if not user:
            # New user - create account
            user = User(
                google_id=google_id,
                email=email,
                name=name,
                profile_pic=picture
            )
            user.save()

        # Log the user in
        login_user(user)

        # Redirect based on whether they need onboarding
        if not user.has_completed_onboarding:
            return redirect(url_for('user.onboarding'))
        return redirect(url_for('chat.index'))

    except Exception as e:
        current_app.logger.error(f"Google callback error: {e}")
        return redirect(url_for('auth.login', error="Google login failed"))

# @app.route('/auth/signup', methods=['POST'])
# def signup():   
#     """Handle new user registration"""
#     data = request.get_json()
#     # Create new user (implement your registration logic)
#     user = User(id=data['email'], has_completed_onboarding=False)
#     login_user(user)
#     return jsonify({'success': True})

# @app.route('/auth/logout')
# @login_required
# def logout():
#     """Handle user logout"""
#     logout_user()
#     return redirect(url_for('landing'))

@login_manager.user_loader
def load_user(user_id):
    # User loader for Flask-Login
    # Implement user loading from your database
    return User(user_id)
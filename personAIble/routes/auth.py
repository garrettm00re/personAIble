from flask import Blueprint, redirect, url_for, current_app, request
#from flask_login import login_user, login_required, logout_user, current_user
from ..extensions import oauth, db, qdrant_client
from user import User
from utils import encrypt_user_id, decrypt_user_id, get_user_from_request
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/google')
def google_login():
    user = get_user_from_request(request, db)
    if user:
        if not user.onboarded:
            return redirect(url_for('onboarding.onboarding'))
        else:
            return redirect(url_for('main.main'))
    
    redirect_uri = url_for('auth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route('/auth/google/callback')
def google_callback():
    try:
        token = oauth.google.authorize_access_token()
        resp = oauth.google.get('https://openidconnect.googleapis.com/v1/userinfo')
        user_info = resp.json()

        google_id = user_info.get('sub')
        email = user_info.get('email')
        first_name = user_info.get('given_name')
        last_name = user_info.get('family_name')
        picture = user_info.get('picture')

        user = db.get_by_google_id(google_id)
        if not user:
            user = User(google_id=google_id, email=email, first_name=first_name,
                        last_name=last_name, profile_pic=picture)
            db.save(user)
            
        # Instead of login_user, encrypt the user ID
        encrypted_id = encrypt_user_id(google_id)
        
        if not user.onboarded:
            return redirect(f'/onboarding?uid={encrypted_id}')
        return redirect(f'/app?uid={encrypted_id}')

    except Exception as e:
        current_app.logger.error(f"Google callback error: {e}")
        return redirect('/auth/google')

@auth_bp.route('/auth/logout')
def logout():
    return redirect('/')  # Just redirect, no state to clear 
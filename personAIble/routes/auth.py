from flask import Blueprint, redirect, url_for, current_app
from flask_login import login_user, login_required, logout_user, current_user
from ..extensions import oauth, db
from user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/google')
def google_login():
    if current_user.is_authenticated:
        if not current_user.onboarded:
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
            db.save(User(google_id=google_id, email=email, first_name=first_name,
                        last_name=last_name, profile_pic=picture))
        
        login_user(user)

        if not user.onboarded:
            return redirect(url_for('onboarding.onboarding'))
        return redirect(url_for('main.main'))

    except Exception as e:
        current_app.logger.error(f"Google callback error: {e}")
        return redirect(url_for('auth.google_login', error="Google login failed"))

@auth_bp.route('/auth/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.landing')) 
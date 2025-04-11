from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from utils import decrypt_user_id  # You'll need to implement this

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def landing():
    user_id = request.args.get('uid')
    if user_id:
        try:
            google_id = decrypt_user_id(user_id)
            user = db.get_by_google_id(google_id)
            if not user:
                return redirect('/') ## ?
            if not user.onboarded:
                return redirect(f'/onboarding?uid={user_id}')
        except:
            pass  # Invalid/expired token, show landing
    return render_template('landing.html')

@main_bp.route('/app')
def main():
    user_id = request.args.get('uid')
    if not user_id:
        return redirect('/')
    
    try:
        google_id = decrypt_user_id(user_id)
        user = db.get_by_google_id(google_id)
        if not user.onboarded:
            return redirect(f'/onboarding?uid={user_id}')
        return render_template('app2.html', user_id=user_id)
    except:
        return redirect('/') 
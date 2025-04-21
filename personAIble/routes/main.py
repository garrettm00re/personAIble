from flask import Blueprint, render_template, redirect, url_for, request
# from flask_login import login_required, current_user
from utils import decrypt_user_id, get_user_from_request
from ..extensions import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def landing():
    user = get_user_from_request(request, db)
    if user:
        if not user.onboarded:
            return redirect(f'/onboarding?uid={user.google_id}')
        else:
            return redirect(f'/app?uid={user.google_id}')
    return render_template('landing.html')

@main_bp.route('/app/')
def main():
    print("MAIN")
    user = get_user_from_request(request, db)
    if not user:
        print("REDIRECTING TO LANDING")
        return redirect('/')
    
    if not user.onboarded:
        print("REDIRECTING TO ONBOARDING")
        return redirect(f'/onboarding?uid={user.google_id}')
    # return render_template('app2.html', user_id=user.google_id)
    print("RENDERING APP")
    return render_template('app2.html')
 
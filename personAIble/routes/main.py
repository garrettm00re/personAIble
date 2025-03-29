from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def landing():
    if current_user.is_authenticated:
        if not current_user.onboarded:
            return redirect(url_for('onboarding.onboarding'))
        else:
            return redirect(url_for('main.main'))
    return render_template('landing.html')

@main_bp.route('/app')
@login_required
def main():
    if not current_user.onboarded:
        return redirect(url_for('onboarding.onboarding'))
    return render_template('app.html') 
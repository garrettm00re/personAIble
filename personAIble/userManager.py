from .extensions import login_manager, db

@login_manager.user_loader
def load_user(user_id: str):
    """User loader for Flask-Login"""
    return db.get_by_google_id(user_id)
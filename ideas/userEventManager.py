from functools import wraps
from typing import Callable, List
from datetime import datetime
from flask import session
from flask_login import user_logged_in, user_logged_out
import atexit

class UserEventManager:
    def __init__(self):
        # Lists to store callback functions
        self._login_callbacks: List[Callable] = []
        self._logout_callbacks: List[Callable] = []
        
        # Track active sessions
        self.active_sessions = {}  # user_id -> last_active
        
    def on_login(self, f: Callable) -> Callable:
        """Decorator to register login callbacks"""
        @wraps(f)
        def wrapped(*args, **kwargs):
            return f(*args, **kwargs)
        self._login_callbacks.append(f)
        return wrapped
        
    def on_logout(self, f: Callable) -> Callable:
        """Decorator to register logout callbacks"""
        @wraps(f)
        def wrapped(*args, **kwargs):
            return f(*args, **kwargs)
        self._logout_callbacks.append(f)
        return wrapped
        
    def _handle_login(self, user):
        """Internal method to execute all login callbacks"""
        self.active_sessions[user.google_id] = datetime.utcnow()
        for callback in self._login_callbacks:
            try:
                callback(user)
            except Exception as e:
                app.logger.error(f"Login callback error: {e}")
                
    def _handle_logout(self, user):
        """Internal method to execute all logout callbacks"""
        self.active_sessions.pop(user.google_id, None)
        for callback in self._logout_callbacks:
            try:
                callback(user)
            except Exception as e:
                app.logger.error(f"Logout callback error: {e}")

# Create singleton instance
user_events = UserEventManager()

# Register Flask-Login signals
@user_logged_in.connect_via(app)
def on_user_logged_in(sender, user):
    user_events._handle_login(user)

@user_logged_out.connect_via(app)
def on_user_logged_out(sender, user):
    user_events._handle_logout(user)

# Session cleanup
@app.before_request
def check_session_activity():
    if current_user.is_authenticated:
        last_active = user_events.active_sessions.get(current_user.google_id)
        if last_active:
            # Update last active time
            user_events.active_sessions[current_user.google_id] = datetime.utcnow()

# Socket.IO disconnect handler
@socketio.on('disconnect')
def handle_disconnect():
    if current_user.is_authenticated:
        user_events._handle_logout(current_user)

# Cleanup on server shutdown
@atexit.register
def cleanup_sessions():
    for user_id in list(user_events.active_sessions.keys()):
        try:
            # Simulate a user object for cleanup
            user = User(google_id=user_id)
            user_events._handle_logout(user)
        except Exception as e:
            app.logger.error(f"Cleanup error: {e}")

# Example usage:
@user_events.on_login
def handle_user_login(user):
    """Called when user logs in"""
    print(f"User {user.google_id} logged in")
    # Initialize user-specific resources
    
@user_events.on_logout
def handle_user_logout(user):
    """Called when user logs out or session ends"""
    print(f"User {user.google_id} logged out")
    # Cleanup user-specific resources
from flask import Flask
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth
import os

# Initialize extensions
login_manager = LoginManager()
oauth = OAuth()

def create_app():
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Config
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    
    # Initialize extensions
    login_manager.init_app(app)
    oauth.init_app(app)
    
    # Register blueprints
    from .auth import auth_bp
    from .chat import chat_bp
    from .user import user_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(user_bp)
    
    return app
from flask import Flask
from .routes.auth import auth_bp
from .routes.main import main_bp
from .routes.onboarding import onboarding_bp
from .routes.api import api_bp
from . import userManager  # Import userManager to register the user loader
# from .sockets import handlers  # Import socket handlers
import os
from dotenv import load_dotenv
from .extensions import oauth # socketio, 

load_dotenv()

def create_app():
    app = Flask(__name__, 
                template_folder='../templates', 
                static_folder='../static')
    
    # Config
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    
    # Initialize extensions
    # socketio.init_app(app)
    # login_manager.init_app(app)
    # login_manager.login_view = 'main.landing'
    
    # Initialize OAuth
    oauth.init_app(app)
    oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile',
            'prompt': 'select_account'
        }
    )
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(onboarding_bp)
    app.register_blueprint(api_bp)
    
    return app

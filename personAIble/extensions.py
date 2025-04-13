from flask_socketio import SocketIO
# from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth
from database import Database
from qaModel import PersonAIble
from qdrant_client import qdrant
# Initialize extensions
socketio = SocketIO(cors_allowed_origins="*")
# login_manager = LoginManager()
oauth = OAuth()
db = Database()
ai_model = PersonAIble()
ai_model.db_client = db.db_client

# Global state (getting nuked, slowly but surely)
followupAnswers = {}  # google_id : (answer, success)
vector_stores = {}  # google_id : vector_store
followUpTimeout = 300  # seconds 
from flask_socketio import SocketIO
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth
from database import Database
from qaModel import PersonAIble
from qdrant_client import QdrantClient
from qdrant_client.http import models
import os

# Initialize extensions
socketio = SocketIO(cors_allowed_origins="*")
login_manager = LoginManager()
oauth = OAuth()
db = Database()
ai_model = PersonAIble()
ai_model.db_client = db.db_client

# Initialize Qdrant client (like other extensions)
qdrant = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

# Global state
followupAnswers = {}  # google_id : (answer, success)
vector_stores = {}  # google_id : vector_store
followUpTimeout = 300  # seconds 
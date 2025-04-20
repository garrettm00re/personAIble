from authlib.integrations.flask_client import OAuth
from database import Database
from qaModel import PersonAIble
from clients import qdrant
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Initialize extensions
oauth = OAuth()
db = Database()

# Initialize embeddings and llm
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
llm = ChatOpenAI(model="chatgpt-4o-latest")
qdrant_client = qdrant(embeddings)

ai_model = PersonAIble(embeddings, llm, qdrant_client) 
ai_model.db_client = db.db_client


# Global state (getting nuked, slowly but surely)
followupAnswers = {}  # google_id : (answer, success)
vector_stores = {}  # google_id : vector_store
followUpTimeout = 300  # seconds 
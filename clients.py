# Create a new file: config/qdrant_client.py
from qdrant_client import QdrantClient
import os
from qdrant_client.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore
from database import Database

class qdrant():
    def __init__(self, embeddings):
        self.url = os.getenv("QDRANT_URL")
        self.api_key = os.getenv("QDRANT_API_KEY")
        self.embeddingDimension = 1536
        self.distance = Distance.COSINE
        self.client = QdrantClient(
            url=self.url,
            api_key=self.api_key
        )
        self.embeddings = embeddings

    def create_user_collection(self, google_id):
        self.client.create_collection(
            collection_name=f"user_{google_id}",
            vectors_config=VectorParams(size=self.embeddingDimension, distance=self.distance),
            timeout=10
        )
    
    def add_onboarding_documents(self, google_id, documents):
        self.client.add_documents(
            collection_name=f"user_{google_id}",
            documents=documents
        )

    def delete_user_collection(self, google_id):
        self.client.delete_collection(collection_name=f"user_{google_id}")
    
    def get_langchain_collection(self, google_id, embeddings):
        return QdrantVectorStore.from_existing_collection(
            url=self.url,
            collection_name=f"user_{google_id}",
            embeddings=embeddings
        )
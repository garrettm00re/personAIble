# Create a new file: config/qdrant_client.py
from qdrant_client import QdrantClient
import os
from qdrant_client.models import Distance, VectorParams, PointStruct
from langchain_qdrant import QdrantVectorStore
from database import Database

class qdrant():
    def __init__(self, embeddings):
        self.url = os.getenv("QDRANT_URL")
        self.api_key = os.getenv("QDRANT_API_KEY")
        self.embeddingDimension = int(os.getenv("EMBEDDING_SIZE", 3072))
        self.distance = Distance.COSINE
        self.client = QdrantClient(
            url=self.url,
            api_key=self.api_key
        )
        self.embeddings = embeddings

    def create_user_collection(self, google_id):
        try:
            self.client.create_collection(
                collection_name=f"user_{google_id}",
                vectors_config=VectorParams(size=self.embeddingDimension, distance=self.distance),
                timeout=10
            )
        except Exception as e:
            print(f"Error creating collection: {e}")
    
    def add_onboarding_documents(self, google_id, documents):
        # Convert to vectors and points
        texts = [doc.page_content for doc in documents] 
        embeddings = self.embeddings.embed_documents(texts)
        
        # Upload to Qdrant
        self.client.upsert(
            collection_name=f"user_{google_id}",
            points=[
                PointStruct(
                    id=idx,
                    vector=embedding,
                    payload={"text": text}
                )
                for idx, (embedding, text) in enumerate(zip(embeddings, texts))
            ]
        )

    def delete_user_collection(self, google_id):
        self.client.delete_collection(collection_name=f"user_{google_id}")
    
    def get_langchain_collection(self, google_id, embeddings):
        return QdrantVectorStore.from_existing_collection(
            url=self.url,
            collection_name=f"user_{google_id}",
            embeddings=embeddings
        )
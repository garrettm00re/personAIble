from qdrant_client.http import models
import os
from clients import qdrant
from .extensions import ai_model

def create_user_collection(google_id: str, documents):
    collection_name = f"user_{google_id}"
    
    # Create collection with same dimensions as your embeddings
    qdrant.recreate_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=int(os.getenv("EMBEDDING_SIZE")),  # OpenAI embedding size
            distance=models.Distance.COSINE
        )
    )
    
    # Add documents
    vectors = []
    for doc in documents:
        embedding = ai_model.embeddings.embed_query(doc.page_content)
        vectors.append(models.PointStruct(
            id=hash(doc.page_content),  # or use sequential IDs
            vector=embedding,
            payload={"text": doc.page_content, "metadata": doc.metadata}
        ))
    
    # Upload in batches
    BATCH_SIZE = 100
    for i in range(0, len(vectors), BATCH_SIZE):
        batch = vectors[i:i + BATCH_SIZE]
        qdrant.upsert(
            collection_name=collection_name,
            points=batch
        )
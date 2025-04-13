# Create a new file: config/qdrant_client.py
from qdrant_client import QdrantClient
import os

qdrant = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)
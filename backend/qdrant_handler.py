"""Thin wrapper around Qdrant for upserting and searching multimodal nodes."""
import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct


class QdrantHandler:
    def __init__(self, collection_name, dim=768, location=":memory:"):
        self.client = QdrantClient(location=location)
        self.collection_name = collection_name

        if not self.client.collection_exists(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
            )

    def upload(self, nodes):
        """Upsert LlamaIndex nodes (each with .embedding, .metadata, .json())."""
        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=node.embedding,
                payload={**node.metadata, "_node_content": node.json()},
            )
            for node in nodes
        ]
        self.client.upsert(collection_name=self.collection_name, points=points)

    def search(self, vector, top_k=5):
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=vector,
            limit=top_k * 10,
            with_payload=True,
        )
        return results.points

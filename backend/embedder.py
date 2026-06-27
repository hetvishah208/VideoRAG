"""Embed text and images into a shared CLIP vector space."""
import os

from PIL import Image
from sentence_transformers import SentenceTransformer


class EmbeddingProcessor:
    def __init__(self, model_name="clip-ViT-L-14"):
        self.model = SentenceTransformer(model_name)

    def embed_text(self, text):
        return self.model.encode(text, normalize_embeddings=True)

    def embed_image(self, image_path):
        img = Image.open(image_path).convert("RGB").resize((224, 224))
        return self.model.encode([img], normalize_embeddings=True)[0]

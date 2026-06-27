"""Central configuration for the VideoRAG pipeline.

All values can be overridden via environment variables so the same code
runs locally, in CI, or in a container without edits.
"""
import os

# --- Qdrant ---
# ":memory:" = ephemeral in-process store (data lost on restart).
# Use a URL like "http://localhost:6333" for a persistent local server.
QDRANT_LOCATION = os.getenv("QDRANT_LOCATION", ":memory:")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "multimodal_video_data")

# --- Models ---
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "clip-ViT-L-14")   # sentence-transformers
TRANSCRIPTION_MODEL = os.getenv("TRANSCRIPTION_MODEL", "base")    # faster-whisper
VECTOR_DIM = int(os.getenv("VECTOR_DIM", "768"))                  # clip-ViT-L-14 -> 768

# --- LLM (OpenRouter, OpenAI-compatible) ---
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen/qwen2.5-vl-72b-instruct:free")
API_KEY = os.getenv("API_KEY")  # set in .env; never commit

# --- Frame extraction ---
FRAME_RATE = int(os.getenv("FRAME_RATE", "2"))  # frames sampled per second

# --- Text chunking ---
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "200"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))

# --- Retrieval ---
TOP_K = int(os.getenv("TOP_K", "5"))
MIN_SCORE = float(os.getenv("MIN_SCORE", "0.7"))

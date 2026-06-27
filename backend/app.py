"""FastAPI surface for VideoRAG.

Endpoints:
  POST /ingest  -> process a folder of videos into the index
  POST /query   -> ask a question against the indexed videos

A simple X-API-Key header guards both endpoints. State (the Qdrant index and
embedder) is held in-process for the lifetime of the server.
"""
import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import config
from pipeline import ingest_videos, answer_query

load_dotenv()

app = FastAPI(title="VideoRAG API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-process state populated by /ingest and consumed by /query.
_state = {"qdrant": None, "embedder": None}


def verify_api_key(x_api_key: str = Header(...)):
    if not config.API_KEY or x_api_key != config.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )


class IngestRequest(BaseModel):
    video_folder: str
    working_dir: str


class QueryRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "ok", "indexed": _state["qdrant"] is not None}


@app.post("/ingest")
def ingest(req: IngestRequest, _=Depends(verify_api_key)):
    qdrant, embedder = ingest_videos(req.video_folder, req.working_dir)
    _state["qdrant"], _state["embedder"] = qdrant, embedder
    return {"status": "indexed", "video_folder": req.video_folder}


@app.post("/query")
def query(req: QueryRequest, _=Depends(verify_api_key)):
    if _state["qdrant"] is None:
        raise HTTPException(status_code=409, detail="No videos indexed yet. Call /ingest first.")
    return answer_query(_state["qdrant"], _state["embedder"], req.query)

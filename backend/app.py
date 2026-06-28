"""FastAPI surface for VideoRAG.

Endpoints:
  POST /upload  -> accept a video file, ingest it, return a preview URL
  POST /query   -> ask a question against the indexed videos
  GET  /videos/{filename} -> serve uploaded videos back to the frontend
  GET  /health  -> liveness check
"""
import os
import shutil
import tempfile

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
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

# In-process state populated by /upload and consumed by /query.
_state = {"qdrant": None, "embedder": None}

# Persistent directories for uploaded videos and processing artifacts.
UPLOAD_DIR = os.path.join(tempfile.gettempdir(), "videorag_uploads")
WORK_DIR = os.path.join(tempfile.gettempdir(), "videorag_work")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(WORK_DIR, exist_ok=True)


class QueryRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "ok", "indexed": _state["qdrant"] is not None}


@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    """Accept a video file, save it, run the full ingestion pipeline,
    and return a URL the frontend can use for video preview."""

    if not file.filename or not file.filename.lower().endswith(".mp4"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .mp4 files are supported.",
        )

    # Clear previous uploads and work artifacts for a clean run.
    for d in (UPLOAD_DIR, WORK_DIR):
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d, exist_ok=True)

    # Save the uploaded file to disk.
    save_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(save_path, "wb") as f:
        while chunk := await file.read(1024 * 1024):  # 1 MB chunks
            f.write(chunk)

    # Run the full ingestion pipeline.
    try:
        qdrant, embedder = ingest_videos(UPLOAD_DIR, WORK_DIR)
        _state["qdrant"], _state["embedder"] = qdrant, embedder
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion failed: {str(e)}",
        )

    return {
        "status": "indexed",
        "filename": file.filename,
        "url": f"/videos/{file.filename}",
    }


@app.get("/videos/{filename}")
def serve_video(filename: str):
    """Serve an uploaded video file back to the frontend for preview."""
    path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="Video not found")
    return FileResponse(path, media_type="video/mp4")


@app.post("/query")
def query(req: QueryRequest):
    if _state["qdrant"] is None:
        raise HTTPException(
            status_code=409,
            detail="No videos indexed yet. Upload a video first.",
        )
    return answer_query(_state["qdrant"], _state["embedder"], req.query)
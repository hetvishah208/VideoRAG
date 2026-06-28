# VideoRAG — Ask Questions About Any Video Using AI

**Upload a video. Ask a question in plain English. Get an answer grounded in what was actually said and shown — with the relevant timestamp.**

VideoRAG is a multimodal Retrieval-Augmented Generation system that lets you query long-form video content using natural language. It doesn't just search transcripts — it understands both what was **spoken** and what was **shown on screen**, combining transcript snippets with visually relevant keyframes to produce accurate, grounded answers.

> **Example:** Upload a 3-minute explainer about computer components. Ask *"where can I buy a computer?"* — and the system correctly responds that the video discusses internal components, not purchasing. No hallucination. No made-up answers.

---

## The Problem

Video content is one of the hardest formats to search. You can't Ctrl+F a video. Existing tools either:

- **Transcript-only search** — misses visual content entirely (diagrams, charts, demonstrations)
- **Timestamp-based chapter markers** — require manual effort and only give you rough sections, not precise answers
- **Generic summarization** — loses the specific details you're actually looking for

If you've ever scrubbed through a 30-minute tutorial looking for the 15 seconds where the presenter explained one specific thing, you've felt this problem.

## What VideoRAG Does Differently

VideoRAG treats video as a **multimodal document** — both the audio transcript and the visual frames are first-class citizens in retrieval. When you ask a question:

1. Your query is embedded into the same vector space as both transcript chunks and keyframes
2. The system retrieves the most semantically relevant transcript snippets
3. For each snippet, it finds the **temporally closest keyframe** from the same video — so the visual context actually matches the spoken context
4. A vision-language model synthesizes an answer from both modalities, grounded in what the video actually contains

If the answer isn't in the video, the system says so instead of hallucinating.

---

## Architecture

```
.mp4 ──┬──► Frame Sampling (OpenCV, 2fps)        ──► Keyframes ──┐
       │                                                          │
       └──► Audio Extraction (MoviePy)                            │
                 └──► Transcription (faster-whisper, int8)        │
                           └──► Chunking (LangChain, 200-token)   │
                                                                  ▼
                           CLIP ViT-L/14 Embeddings (text + image)
                                                                  │
                                                                  ▼
                                    Qdrant Vector Index (cosine similarity)
                                                                  │
    User Query ──► CLIP text embedding ──► Top-K retrieval ───────┤
                                                                  ▼
                  Transcript chunks + temporally aligned keyframes
                                                                  │
                                                                  ▼
                    Vision-Language Model (OpenRouter) ──► Grounded answer
```

**Key design decision:** Retrieved transcript chunks are paired with keyframes by **timestamp proximity within the same video**, not by embedding similarity. This ensures the visual context the LLM sees actually corresponds to what was being discussed at that point in the video — not just a visually similar but temporally unrelated frame.

---

## Tech Stack

| Layer | Tool | Why |
|---|---|---|
| Transcription | faster-whisper (int8 quantized) | CPU-efficient, accurate speech-to-text |
| Frame Extraction | OpenCV | Reliable, no GPU required |
| Audio Extraction | MoviePy | Clean .mp4 → .mp3 conversion |
| Embeddings | CLIP ViT-L/14 via sentence-transformers | Shared text-image vector space — the core of multimodal retrieval |
| Text Chunking | LangChain RecursiveCharacterTextSplitter | 200-token chunks, 50-token overlap for context continuity |
| Vector Store | Qdrant (in-memory) | Fast cosine similarity search, no external server needed |
| Index Nodes | LlamaIndex TextNode / ImageNode | Structured metadata (timestamps, video IDs, source files) |
| LLM | OpenRouter (OpenAI-compatible) | Free-tier vision models, no GPU required locally |
| Backend API | FastAPI | File upload, ingestion orchestration, query endpoint |
| Frontend | React + Vite + TypeScript | Video preview, query interface, answer display |

**Total cost: $0.** Everything runs locally on CPU except the final LLM call, which uses OpenRouter's free-tier vision models.

---

## Screenshots

Please have a look at the example screenshots in the Screenshots folder showing video upload, query answering, and out-of-scope detection.

---

## Project Structure

```
videorag/
├── backend/
│   ├── app.py                  # FastAPI server (/upload, /query, /health, /videos)
│   ├── pipeline.py             # Ingestion + query orchestration (also works as CLI)
│   ├── config.py               # Environment-driven configuration
│   ├── frame_extractor.py      # OpenCV keyframe sampling at configurable FPS
│   ├── audio_extractor.py      # MoviePy .mp4 → .mp3 extraction
│   ├── transcriber.py          # faster-whisper speech-to-text
│   ├── embedder.py             # CLIP ViT-L/14 text + image embedding
│   ├── text_image_indexer.py   # Chunking + LlamaIndex node creation
│   ├── qdrant_handler.py       # Qdrant vector store operations
│   ├── searcher.py             # Multimodal retrieval with temporal alignment
│   ├── llm_service.py          # Vision-LLM answer synthesis via OpenRouter
│   ├── utils.py                # Timestamp parsing utilities
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.tsx             # Main layout
│   │   ├── components/
│   │   │   ├── VideoUpload.tsx  # File upload + ingestion trigger
│   │   │   ├── QueryInput.tsx   # Search bar + query submission
│   │   │   └── AnswerDisplay.tsx # Answer rendering
│   │   └── lib/
│   │       └── api.ts          # Typed API client
│   ├── package.json
│   └── .env.example
├── README.md
├── LICENSE
└── .gitignore
```

---

## Setup — Step by Step

Tested on Windows 11 with Python 3.11, 16GB RAM, CPU-only (Intel Iris Xe). Works on macOS/Linux with the same steps (use `python3` instead of `py`).

### Prerequisites

- **Python 3.10+** — check with `py --version` (Windows) or `python3 --version` (macOS/Linux)
- **Node.js 18+** — check with `node --version`
- **OpenRouter API key** — free, no credit card needed. Get one at [openrouter.ai/keys](https://openrouter.ai/keys)

### 1. Clone the repo

```bash
git clone https://github.com/hetvishah208/videorag.git
cd videorag
```

### 2. Backend setup

```bash
cd backend

# Create virtual environment
py -m venv .venv                    # Windows
# python3 -m venv .venv             # macOS/Linux

# Activate it
.venv\Scripts\activate              # Windows
# source .venv/bin/activate          # macOS/Linux

# Install dependencies (~5-10 min first time — downloads PyTorch, CLIP, whisper)
pip install -r requirements.txt
pip install langchain-text-splitters

# Configure environment
cp .env.example .env
# Open .env and add your OpenRouter API key:
#   API_KEY=your_openrouter_key_here
#   LLM_MODEL=google/gemma-4-31b-it:free

# Start the server
uvicorn app:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

Verify: open **http://localhost:8000/health** in your browser → `{"status":"ok","indexed":false}`

### 3. Frontend setup

Open a **new terminal** (keep the backend running):

```bash
cd frontend
npm install

# Configure environment
cp .env.example .env
# Open .env and set:
#   VITE_API_BASE_URL=http://localhost:8000

# Start the dev server
npm run dev
```

You should see:
```
VITE v6.x.x ready
➜  Local: http://localhost:5173/
```

### 4. Use it

1. Open **http://localhost:5173** in your browser
2. Click **Choose File** and select an `.mp4` video
3. Wait for indexing to complete (status shows "Indexed: your_video.mp4")
   - First run downloads CLIP ViT-L/14 (~1.7GB) — cached after that
   - A 3-minute video takes ~2-5 minutes to index on CPU
4. Type a question and click **Search**
5. Read the grounded answer

### CLI mode (no frontend needed)

You can also run the pipeline directly from the command line:

```bash
cd backend
py pipeline.py --videos "./my_videos" --workdir "./scratch" --query "What is this video about?"
```

---

## Configuration

All backend settings are environment-driven. Override any of these in `backend/.env`:

| Variable | Default | Description |
|---|---|---|
| `API_KEY` | *(required)* | OpenRouter API key |
| `LLM_MODEL` | `google/gemma-4-31b-it:free` | Vision-LLM for answer synthesis |
| `LLM_BASE_URL` | `https://openrouter.ai/api/v1` | OpenAI-compatible endpoint |
| `EMBEDDING_MODEL` | `clip-ViT-L-14` | Sentence-transformers model for embeddings |
| `TRANSCRIPTION_MODEL` | `base` | Faster-whisper model size |
| `FRAME_RATE` | `2` | Keyframes sampled per second |
| `CHUNK_SIZE` | `200` | Transcript chunk size in tokens |
| `CHUNK_OVERLAP` | `50` | Overlap between chunks |
| `TOP_K` | `5` | Number of results to retrieve |
| `MIN_SCORE` | `0.7` | Minimum cosine similarity threshold |
| `QDRANT_LOCATION` | `:memory:` | Qdrant storage (`:memory:` or server URL) |
| `ALLOWED_ORIGINS` | `http://localhost:5173` | CORS origins for the frontend |

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/upload` | Upload an .mp4 file → runs full ingestion pipeline |
| `POST` | `/query` | `{"query": "your question"}` → grounded answer + timestamps |
| `GET` | `/health` | `{"status": "ok", "indexed": true/false}` |
| `GET` | `/videos/{filename}` | Serves uploaded video for frontend preview |

---

## Design Decisions

**Why CLIP for both modalities?**
CLIP maps text and images into the same 768-dimensional vector space. This means a text query like "circuit board" is directly comparable to an image of a circuit board — no separate image search pipeline needed. The alternative (separate text embedder + image captioning + text search over captions) loses visual nuance and adds latency.

**Why temporal alignment instead of embedding similarity for frame selection?**
When retrieving context for a transcript chunk at timestamp 1:30, the most useful keyframe is the one showing what was on screen at ~1:30 — not a visually similar frame from 0:15 that happens to show the same object in a different context. Temporal proximity preserves narrative coherence.

**Why in-memory Qdrant?**
For a demo and portfolio project, persistence isn't needed — the user uploads and queries in one session. This eliminates the need to run a separate Qdrant server. For production, set `QDRANT_LOCATION` to a server URL.

**Why OpenRouter instead of local LLM?**
The final answer synthesis benefits from a vision-capable model that can see keyframes. Running a vision LLM locally (e.g., LLaVA 13B) requires a GPU with 10GB+ VRAM. OpenRouter provides free-tier access to vision models like Gemma 4 31B, keeping the project fully runnable on CPU-only hardware.

**Why not LangChain/LlamaIndex for the full pipeline?**
The retrieval logic (embed → search → temporally align frames → synthesize) is straightforward enough that a framework would add dependency weight without simplifying the code. The pipeline is ~200 lines of orchestration across focused modules — readable, debuggable, and framework-independent.

---

## Known Limitations

- **In-memory index.** Data is lost when the server restarts. Each session requires re-uploading and re-indexing. Set `QDRANT_LOCATION` to a Qdrant server URL for persistence.
- **Single-video indexing.** Each upload clears the previous index. Multi-video support would require collection-per-video or metadata filtering.
- **CPU-only processing.** Indexing is slow on CPU (~2-5 min per minute of video). A GPU would reduce this to seconds.
- **Free-tier LLM rate limits.** OpenRouter free models allow ~20 requests/minute and ~200/day. Sufficient for demos, not for production traffic.
- **No streaming answers.** The LLM response arrives all at once. Streaming would improve perceived latency.
- **.mp4 only.** Other video formats would need a preprocessing step or ffmpeg conversion.

---

## Future Improvements

- [ ] Multi-video indexing with per-video metadata filtering
- [ ] Persistent Qdrant storage with collection management
- [ ] Streaming LLM responses for better UX
- [ ] Timestamp-linked video playback (click answer → video seeks to that moment)
- [ ] Retrieval evaluation harness with hit-rate@k metrics
- [ ] Docker Compose for one-command setup

---

## License

MIT — see [LICENSE](LICENSE).
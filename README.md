# VideoRAG — Multimodal Retrieval over Long-Form Video

Ask natural-language questions about a video and get an answer grounded in both
the **spoken transcript** and the **visual frames**, with the relevant
timestamp surfaced for playback.

VideoRAG ingests `.mp4` files, transcribes the audio, samples keyframes,
embeds both modalities into a shared CLIP vector space, and retrieves the most
relevant transcript chunks plus their temporally-aligned frames to ground a
vision-language model's answer.

> Runs entirely on free/open-source components. The only external call is to an
> OpenAI-compatible LLM endpoint (OpenRouter), which offers free-tier vision
> models.

---

## How it works

```
.mp4 ──┬─► frame sampling (OpenCV)         ─► keyframes ─┐
       └─► audio extract (MoviePy)                       │
                └─► transcription (faster-whisper)       │
                          └─► chunking (LangChain)       │
                                                         ▼
                        CLIP ViT-L/14 embeddings (text + image)
                                                         │
                                                         ▼
                                  Qdrant vector index (cosine)
                                                         │
   query ─► CLIP text embedding ─► top-k retrieval ──────┤
                                                         ▼
            transcript chunks + closest-in-time frames
                                                         │
                                                         ▼
              vision-language model (OpenRouter) ─► grounded answer + timestamp
```

A retrieved text chunk is paired with the keyframe from the **same video**
whose timestamp is closest, so the visual context the model sees lines up with
the transcript context.

## Tech stack

| Layer            | Tooling                                            |
|------------------|----------------------------------------------------|
| Transcription    | faster-whisper (int8)                              |
| Frame extraction | OpenCV                                             |
| Embeddings       | CLIP ViT-L/14 via `sentence-transformers`         |
| Chunking         | LangChain `RecursiveCharacterTextSplitter`        |
| Vector store     | Qdrant (`:memory:` by default)                    |
| Indexing nodes   | LlamaIndex `TextNode` / `ImageNode`               |
| LLM              | OpenRouter (OpenAI-compatible), default Qwen2.5-VL |
| API              | FastAPI                                            |
| Frontend         | React + Vite + TypeScript                          |

## Repository layout

```
videorag/
├── backend/            # FastAPI app + ingestion/retrieval pipeline
│   ├── app.py          # API surface (/ingest, /query, /health)
│   ├── pipeline.py     # orchestration + CLI entrypoint
│   ├── searcher.py     # multimodal retrieval
│   ├── llm_service.py  # answer synthesis
│   ├── *.py            # extractors, embedder, indexer, qdrant handler
│   └── requirements.txt
└── frontend/           # React + Vite UI
    └── src/
```

## Quickstart

### 1. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env        # then add your OpenRouter API key
uvicorn app:app --reload    # serves on http://localhost:8000
```

Run the pipeline directly from the CLI (no server needed):

```bash
python pipeline.py --videos ./my_videos --workdir ./scratch --query "What is the video about?"
```

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env        # set VITE_API_BASE_URL and VITE_API_KEY
npm run dev                 # serves on http://localhost:5173
```

## Configuration

All backend settings are environment-driven (see `backend/.env.example`):
embedding model, transcription model, frame rate, chunk size/overlap, `top_k`,
similarity threshold, Qdrant location, and LLM model. Defaults work out of the box.

## Notes & limitations

- **In-memory index by default.** With `QDRANT_LOCATION=:memory:`, the index is
  rebuilt per process and lost on restart. Point it at a running Qdrant server
  for persistence.
- **Single-process state.** The API holds the index in memory after `/ingest`;
  this is intentional for a demo and would move to a shared store for multi-worker
  deployments.
- **Timestamps from filenames.** Frame timestamps are parsed from the
  `HH-MM-SS_index.jpg` naming convention written during extraction.

## License

MIT — see [LICENSE](LICENSE).

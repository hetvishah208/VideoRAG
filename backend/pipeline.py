"""End-to-end ingestion and query orchestration for VideoRAG."""
import os

import config
from frame_extractor import FrameExtractor
from audio_extractor import AudioExtractor
from transcriber import AudioTranscriber
from embedder import EmbeddingProcessor
from text_image_indexer import TextImageIndexer
from qdrant_handler import QdrantHandler
from searcher import MultimodalSearcher
from llm_service import call_llm


def ingest_videos(video_folder, working_dir):
    """Process every .mp4 in `video_folder` into a searchable Qdrant index.

    Returns (qdrant_handler, embedder) so the same in-memory index can be
    reused for querying within a single process.
    """
    frame_dir = os.path.join(working_dir, "Frames")
    audio_dir = os.path.join(working_dir, "Audio")
    transcript_dir = os.path.join(working_dir, "Transcript")

    FrameExtractor(config.FRAME_RATE).extract_frames(video_folder, frame_dir)
    AudioExtractor().extract_audio(video_folder, audio_dir)
    AudioTranscriber(config.TRANSCRIPTION_MODEL).transcribe(audio_dir, transcript_dir)

    embedder = EmbeddingProcessor(config.EMBEDDING_MODEL)
    indexer = TextImageIndexer(embedder, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
    nodes = indexer.index_text(transcript_dir) + indexer.index_images(frame_dir)

    qdrant = QdrantHandler(
        config.COLLECTION_NAME,
        dim=config.VECTOR_DIM,
        location=config.QDRANT_LOCATION,
    )
    qdrant.upload(nodes)
    return qdrant, embedder


def answer_query(qdrant, embedder, query):
    """Retrieve multimodal context for `query` and synthesize an answer."""
    searcher = MultimodalSearcher(qdrant, embedder, config.COLLECTION_NAME)
    results = searcher.search(query, top_k=config.TOP_K, min_score=config.MIN_SCORE)

    if not results["text"]:
        return {
            "synthesized_answer": "No relevant content found in the indexed videos.",
            "start_timestamp": None,
            "end_timestamp": None,
        }

    return call_llm(query, results)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ingest videos and run a query.")
    parser.add_argument("--videos", required=True, help="Folder containing .mp4 files")
    parser.add_argument("--workdir", required=True, help="Scratch folder for outputs")
    parser.add_argument("--query", required=True, help="Question to ask")
    args = parser.parse_args()

    qd, emb = ingest_videos(args.videos, args.workdir)
    print(answer_query(qd, emb, args.query)["synthesized_answer"])

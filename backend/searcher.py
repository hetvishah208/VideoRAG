"""Multimodal retrieval: find the best transcript chunks for a query and
attach the visually closest keyframe (by timestamp) from the same video.
"""
import json

from utils import extract_frame_time_from_filename


class MultimodalSearcher:
    def __init__(self, qdrant_handler, embedder, collection_name):
        self.qdrant = qdrant_handler
        self.embedder = embedder
        self.collection_name = collection_name

    def search(self, query, top_k=5, min_score=0.7):
        """Return {"text": [...], "images": [...]} for the given query.

        Text nodes are scored by semantic similarity; each retained text node is
        paired with the keyframe from the same video whose timestamp is closest.
        Returns empty lists when nothing clears `min_score`.
        """
        query_vec = self.embedder.embed_text(query)
        results = self.qdrant.search(query_vec, top_k=top_k)

        text_results, image_results = [], []
        for res in results:
            payload = res.payload
            content = json.loads(payload.get("_node_content", "{}"))
            node_type = payload.get("type")

            if node_type == "text":
                text_results.append({
                    "text": content.get("text", ""),
                    "timestamp": float(payload.get("timestamp", 0)),
                    "video_id": payload.get("video_id", "unknown"),
                    "score": res.score,
                })
            elif node_type == "image":
                frame = payload.get("source", "")
                image_results.append({
                    "path": content.get("image", payload.get("image_path", "")),
                    "frame": frame,
                    "video_id": payload.get("video_id", "unknown"),
                    "timestamp_guess": extract_frame_time_from_filename(frame),
                })

        valid_text = sorted(
            [t for t in text_results if t["score"] >= min_score],
            key=lambda x: -x["score"],
        )[:top_k]

        if not valid_text:
            return {"text": [], "images": []}

        matched_images = []
        for text_node in valid_text:
            same_video = [
                img for img in image_results
                if img["video_id"] == text_node["video_id"]
            ]
            closest = min(
                same_video,
                key=lambda img: abs(img["timestamp_guess"] - text_node["timestamp"]),
                default=None,
            )
            if closest and closest["path"]:
                matched_images.append(closest)

        return {"text": valid_text, "images": matched_images}

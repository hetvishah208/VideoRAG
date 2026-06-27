"""Synthesize a final answer from retrieved transcript snippets and keyframes
using an OpenAI-compatible vision model (served via OpenRouter)."""
from openai import OpenAI

import config


def _build_text_block(prompt, results_final, time_context):
    text_chunks = "\n\n".join(
        f"Text Snippet {i + 1} [{item['timestamp']:.2f}s]:\n{item['text']}"
        for i, item in enumerate(results_final["text"])
    )
    image_refs = "\n".join(
        f"Image Frame {i + 1} (~{img['timestamp_guess']:.2f}s): {img['frame']}"
        for i, img in enumerate(results_final["images"])
    )
    return f"""You are an intelligent VideoRAG interface that answers questions about long-form video content.

You are given transcript excerpts and visual keyframes retrieved by semantic
similarity from a vector database. Use both to infer the user's intent and
produce an accurate, concise answer.

User Question: "{prompt}"

{time_context}

Transcript Snippets:
{text_chunks}

Relevant Frame References (timestamps + filenames; full images sent below):
{image_refs}
"""


def call_llm(prompt, results_final):
    """Return {"synthesized_answer", "start_timestamp", "end_timestamp"}."""
    if not config.API_KEY:
        raise RuntimeError("API_KEY is not set. Add it to backend/.env")

    timestamps = [
        img["timestamp_guess"]
        for img in results_final["images"]
        if "timestamp_guess" in img
    ]
    start_ts = min(timestamps) if timestamps else None
    end_ts = max(timestamps) if timestamps else None
    time_context = (
        f"Relevant video span: ~{start_ts:.2f}s to ~{end_ts:.2f}s."
        if start_ts is not None else ""
    )

    content_blocks = [{"type": "text", "text": _build_text_block(prompt, results_final, time_context)}]
    for img in results_final["images"]:
        if img.get("path"):
            content_blocks.append({
                "type": "image_url",
                "image_url": {"url": img["path"]},
            })

    client = OpenAI(base_url=config.LLM_BASE_URL, api_key=config.API_KEY)
    completion = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=[{"role": "user", "content": content_blocks}],
    )

    return {
        "synthesized_answer": completion.choices[0].message.content,
        "start_timestamp": start_ts,
        "end_timestamp": end_ts,
    }

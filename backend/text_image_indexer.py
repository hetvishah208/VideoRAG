"""Chunk transcripts and load keyframes into embedded LlamaIndex nodes."""
import os

from langchain.text_splitter import RecursiveCharacterTextSplitter
from llama_index.core.schema import TextNode, ImageNode


class TextImageIndexer:
    def __init__(self, embedder, chunk_size=200, chunk_overlap=50):
        self.embedder = embedder
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def index_text(self, transcript_dir):
        nodes = []
        for fname in os.listdir(transcript_dir):
            if not fname.endswith(".txt"):
                continue

            path = os.path.join(transcript_dir, fname)
            with open(path, "r", encoding="utf-8") as f:
                full_text = f.read()

            video_id = os.path.splitext(fname)[0]
            for i, chunk in enumerate(self.splitter.split_text(full_text)):
                node = TextNode(
                    text=chunk,
                    metadata={
                        "type": "text",
                        "video_id": video_id,
                        "source": fname,
                        "chunk_index": i,
                    },
                )
                node.embedding = self.embedder.embed_text(chunk)
                nodes.append(node)
        return nodes

    def index_images(self, frame_dir):
        nodes = []
        for folder in os.listdir(frame_dir):
            folder_path = os.path.join(frame_dir, folder)
            if not os.path.isdir(folder_path):
                continue

            for img_file in os.listdir(folder_path):
                if not img_file.endswith(".jpg"):
                    continue

                img_path = os.path.join(folder_path, img_file)
                node = ImageNode(
                    image=img_path,
                    metadata={
                        "type": "image",
                        "video_id": folder,
                        "source": img_file,
                        "image_path": img_path,
                    },
                )
                node.embedding = self.embedder.embed_image(img_path)
                nodes.append(node)
        return nodes

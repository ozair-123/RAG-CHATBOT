from dataclasses import dataclass
from typing import List, Dict
import re


@dataclass
class ChunkingConfig:
    """Configuration for text chunking."""

    chunk_size: int = 1000
    overlap: int = 200
    min_chunk_size: int = 300


class Chunker:
    """Handles document chunking with sliding window strategy."""

    def __init__(self, config: ChunkingConfig):
        self.config = config

    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Chunk text using sliding window strategy.

        Args:
            text: The text to chunk
            metadata: Optional metadata to attach to each chunk

        Returns:
            List of chunk dictionaries with text and metadata
        """
        chunks = []
        text_length = len(text)

        # If text is shorter than min chunk size, return as single chunk
        if text_length < self.config.min_chunk_size:
            if text.strip():  # Only return if not empty
                chunks.append({"text": text, "metadata": metadata or {}})
            return chunks

        start = 0
        while start < text_length:
            end = start + self.config.chunk_size

            # Don't create chunks smaller than min_chunk_size
            if end >= text_length:
                chunk_text = text[start:]
                if len(chunk_text) >= self.config.min_chunk_size or start == 0:
                    chunks.append({"text": chunk_text, "metadata": metadata or {}})
                break

            chunk_text = text[start:end]
            chunks.append({"text": chunk_text, "metadata": metadata or {}})

            # Move start position with overlap
            start += self.config.chunk_size - self.config.overlap

        return chunks

    def extract_metadata(self, file_path: str, content: str) -> Dict:
        """
        Extract metadata from markdown file.

        Args:
            file_path: Path to the file
            content: File content

        Returns:
            Dictionary with metadata fields
        """
        metadata = {
            "file_path": file_path,
            "heading": "",
            "chapter": "",
            "section": "",
        }

        # Extract first heading (# or ##)
        heading_match = re.search(r"^#{1,2}\s+(.+)$", content, re.MULTILINE)
        if heading_match:
            metadata["heading"] = heading_match.group(1).strip()
            metadata["section"] = heading_match.group(1).strip()

        # Try to extract chapter from file path or heading
        # Assuming structure like "docs/chapter-name/section.md"
        path_parts = file_path.replace("\\", "/").split("/")
        if len(path_parts) >= 2:
            metadata["chapter"] = path_parts[-2]

        return metadata

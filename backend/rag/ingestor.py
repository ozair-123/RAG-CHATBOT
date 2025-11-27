from typing import List, Dict
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from rag.embedder import Embedder
from rag.chunker import Chunker, ChunkingConfig
from utils.file_loader import load_markdown_files
import uuid


class Ingestor:
    """Handles document ingestion pipeline."""

    def __init__(
        self,
        qdrant_client: QdrantClient,
        embedder: Embedder,
        chunking_config: ChunkingConfig,
        collection_name: str,
    ):
        """
        Initialize the ingestor.

        Args:
            qdrant_client: Qdrant client instance
            embedder: Embedder instance
            chunking_config: Chunking configuration
            collection_name: Target collection name
        """
        self.client = qdrant_client
        self.embedder = embedder
        self.chunker = Chunker(chunking_config)
        self.collection_name = collection_name

    async def ingest_documents(self, docs_path: str) -> int:
        """
        Ingest documents from a directory.

        Args:
            docs_path: Path to the documents directory

        Returns:
            Number of chunks ingested
        """
        # Load markdown files
        files = load_markdown_files(docs_path, extensions=[".md", ".mdx"])

        if not files:
            raise ValueError(f"No markdown files found in {docs_path}")

        # Process all files
        all_chunks = []
        for file_info in files:
            chunks = self._process_file(file_info)
            all_chunks.extend(chunks)

        if not all_chunks:
            raise ValueError("No chunks generated from files")

        # Upload chunks to Qdrant
        await self._upload_chunks(all_chunks)

        return len(all_chunks)

    def _process_file(self, file_info: Dict) -> List[Dict]:
        """
        Process a single file into chunks.

        Args:
            file_info: Dictionary with file_path, relative_path, and content

        Returns:
            List of chunk dictionaries
        """
        file_path = file_info["file_path"]
        content = file_info["content"]
        relative_path = file_info["relative_path"]

        # Extract metadata
        metadata = self.chunker.extract_metadata(file_path, content)
        metadata["relative_path"] = relative_path

        # Chunk the content
        chunks = self.chunker.chunk_text(content, metadata)

        return chunks

    async def _upload_chunks(self, chunks: List[Dict]):
        """
        Upload chunks to Qdrant.

        Args:
            chunks: List of chunk dictionaries
        """
        # Extract texts for embedding
        texts = [chunk["text"] for chunk in chunks]

        # Generate embeddings
        embeddings = self.embedder.embed_texts(texts)

        # Create points for Qdrant
        points = []
        for chunk, embedding in zip(chunks, embeddings):
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={"text": chunk["text"], "metadata": chunk["metadata"]},
            )
            points.append(point)

        # Upload to Qdrant in batches
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i : i + batch_size]
            self.client.upsert(collection_name=self.collection_name, points=batch)

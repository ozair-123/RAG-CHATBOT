from typing import List, Dict
from qdrant_client import QdrantClient
from qdrant_client.models import ScoredPoint


class Retriever:
    """Handles vector search and retrieval from Qdrant."""

    def __init__(self, qdrant_client: QdrantClient, collection_name: str):
        """
        Initialize the retriever.

        Args:
            qdrant_client: Qdrant client instance
            collection_name: Name of the collection to search
        """
        self.client = qdrant_client
        self.collection_name = collection_name

    def search(
        self, query_vector: List[float], top_k: int = 5, score_threshold: float = 0.2
    ) -> List[Dict]:
        """
        Search for similar vectors in the collection.

        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            score_threshold: Minimum similarity score

        Returns:
            List of search results with text, metadata, and scores
        """
        search_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k,
            score_threshold=score_threshold,
        )

        results = []
        for result in search_results:
            results.append(
                {
                    "text": result.payload.get("text", ""),
                    "metadata": result.payload.get("metadata", {}),
                    "score": result.score,
                }
            )

        return results

    def format_sources(self, results: List[Dict]) -> List[Dict]:
        """
        Format search results into source citations.

        Args:
            results: List of search results

        Returns:
            List of formatted source dictionaries
        """
        sources = []
        for result in results:
            metadata = result.get("metadata", {})
            sources.append(
                {
                    "file": metadata.get("file_path", "unknown"),
                    "section": metadata.get("section", "unknown"),
                    "score": round(result.get("score", 0.0), 4),
                }
            )
        return sources

from typing import List
import google.generativeai as genai


class Embedder:
    """Handles text embedding generation using Google Gemini."""

    def __init__(self, api_key: str, model: str = "models/text-embedding-004", batch_size: int = 16):
        """
        Initialize the embedder.

        Args:
            api_key: Google API key
            model: Embedding model name
            batch_size: Number of texts to embed in a single batch
        """
        # Configure genai only if not already configured
        if not hasattr(genai, '_configured') or not genai._configured:
            genai.configure(api_key=api_key)
            genai._configured = True
        self.model = model
        self.batch_size = batch_size

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        all_embeddings = []

        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            # Gemini embed_content can handle batches
            result = genai.embed_content(
                model=self.model,
                content=batch,
                task_type="retrieval_document"
            )
            all_embeddings.extend(result["embedding"])

        return all_embeddings

    def embed_single(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        result = genai.embed_content(
            model=self.model,
            content=text,
            task_type="retrieval_query"
        )
        return result["embedding"]

    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings for this model.

        Returns:
            Embedding dimension
        """
        # text-embedding-004 has 768 dimensions
        # text-embedding-003 has 768 dimensions
        if "004" in self.model or "003" in self.model:
            return 768
        else:
            # Default to 768
            return 768

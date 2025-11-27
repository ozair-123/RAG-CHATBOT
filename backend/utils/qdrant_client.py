from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams


def get_qdrant_client(url: str, api_key: str) -> QdrantClient:
    """
    Create and return a Qdrant client.

    Args:
        url: Qdrant instance URL
        api_key: Qdrant API key

    Returns:
        QdrantClient instance
    """
    client = QdrantClient(url=url, api_key=api_key)
    return client


def initialize_collection(
    client: QdrantClient, collection_name: str, vector_size: int
) -> None:
    """
    Initialize a Qdrant collection if it doesn't exist.

    Args:
        client: Qdrant client instance
        collection_name: Name of the collection
        vector_size: Dimension of the embedding vectors
    """
    # Check if collection exists
    collections = client.get_collections().collections
    collection_names = [col.name for col in collections]

    if collection_name not in collection_names:
        # Create collection with cosine distance metric
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
        print(f"Created collection: {collection_name}")
    else:
        print(f"Collection {collection_name} already exists")


def check_collection_exists(client: QdrantClient, collection_name: str) -> bool:
    """
    Check if a collection exists.

    Args:
        client: Qdrant client instance
        collection_name: Name of the collection

    Returns:
        True if collection exists, False otherwise
    """
    collections = client.get_collections().collections
    collection_names = [col.name for col in collections]
    return collection_name in collection_names

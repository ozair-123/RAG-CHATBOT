from fastapi import APIRouter, HTTPException
from api.models import (
    HealthResponse,
    IngestRequest,
    IngestResponse,
    QueryRequest,
    QueryResponse,
    QuerySelectedRequest,
    QuerySelectedResponse,
)
from rag.ingestor import Ingestor
from rag.retriever import Retriever
from rag.embedder import Embedder
from rag.chunker import ChunkingConfig
from agents.agent import BookAgent
from utils.qdrant_client import get_qdrant_client
from config import settings

router = APIRouter()

# Global instances (initialized in main.py startup)
qdrant_client = None
embedder = None
retriever = None
ingestor = None
agent = None


def initialize_components():
    """Initialize all components on startup."""
    global qdrant_client, embedder, retriever, ingestor, agent

    qdrant_client = get_qdrant_client(settings.qdrant_url, settings.qdrant_api_key)
    embedder = Embedder(
        api_key=settings.google_api_key,
        model=settings.embedding_model,
        batch_size=settings.embedding_batch_size,
    )
    retriever = Retriever(
        qdrant_client=qdrant_client, collection_name=settings.collection_name
    )
    chunking_config = ChunkingConfig(
        chunk_size=settings.chunk_size_chars,
        overlap=settings.chunk_overlap_chars,
        min_chunk_size=settings.min_chunk_chars,
    )
    ingestor = Ingestor(
        qdrant_client=qdrant_client,
        embedder=embedder,
        chunking_config=chunking_config,
        collection_name=settings.collection_name,
    )
    agent = BookAgent(api_key=settings.google_api_key, model=settings.llm_model)


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="ok", detail="service running")


@router.post("/ingest", response_model=IngestResponse)
async def ingest_book(request: IngestRequest):
    """
    Ingest book markdown files into the vector database.

    Reads markdown files from the specified path, chunks them,
    generates embeddings, and uploads to Qdrant.
    """
    try:
        chunks_count = await ingestor.ingest_documents(request.docs_path)
        return IngestResponse(status="success", chunks_ingested=chunks_count)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@router.post("/query", response_model=QueryResponse)
async def query_book(request: QueryRequest):
    """
    Query the book using global RAG.

    Retrieves relevant chunks from the vector database and
    generates an answer using the OpenAI agent.
    """
    try:
        # Generate embedding for the question
        question_embedding = embedder.embed_single(request.question)

        # Retrieve relevant chunks
        results = retriever.search(
            query_vector=question_embedding,
            top_k=request.top_k,
            score_threshold=settings.score_threshold,
        )

        # Generate answer using the agent
        answer = await agent.answer_with_context(
            question=request.question, chunks=results, mode=request.mode.value
        )

        # Format sources
        sources = retriever.format_sources(results)

        return QueryResponse(answer=answer, sources=sources)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@router.post("/query-selected", response_model=QuerySelectedResponse)
async def query_selected_text(request: QuerySelectedRequest):
    """
    Query based only on user-selected text.

    Uses only the provided selected text as context,
    without performing vector search.
    """
    try:
        answer = await agent.answer_from_selection(
            question=request.question, selected_text=request.selected_text
        )
        return QuerySelectedResponse(answer=answer)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Selected text query failed: {str(e)}"
        )

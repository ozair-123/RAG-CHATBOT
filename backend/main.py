from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router, initialize_components
from utils.qdrant_client import initialize_collection
from config import settings
from rag.embedder import Embedder

app = FastAPI(
    title="Book RAG Chatbot API",
    description="RAG chatbot for the AI-Driven & Spec-Driven Development Handbook",
    version="1.0.0",
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    print("Initializing components...")

    # Initialize all components
    initialize_components()

    # Initialize Qdrant collection if needed
    from api.routes import qdrant_client, embedder

    if qdrant_client and embedder:
        vector_size = embedder.get_embedding_dimension()
        initialize_collection(
            qdrant_client, settings.collection_name, vector_size
        )

    print("Startup complete!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("Shutting down...")


# Include API routes
app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

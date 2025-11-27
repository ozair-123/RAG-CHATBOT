from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class QueryMode(str, Enum):
    """Query modes for the /query endpoint."""
    answer = "answer"
    explain = "explain"
    summarize = "summarize"


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    detail: str


class IngestRequest(BaseModel):
    """Request body for the /ingest endpoint."""
    docs_path: str = Field(
        ...,
        description="Path to Docusaurus docs folder",
        example="../Ai-Spec-Driven/docs"
    )


class IngestResponse(BaseModel):
    """Response body for the /ingest endpoint."""
    status: str
    chunks_ingested: int


class Source(BaseModel):
    """Source information for a retrieved chunk."""
    file: str
    section: str
    score: float


class QueryRequest(BaseModel):
    """Request body for the /query endpoint."""
    question: str = Field(..., description="Question to ask about the book")
    top_k: int = Field(5, description="Number of chunks to retrieve")
    mode: QueryMode = Field(QueryMode.answer, description="Query mode")


class QueryResponse(BaseModel):
    """Response body for the /query endpoint."""
    answer: str
    sources: List[Source]


class QuerySelectedRequest(BaseModel):
    """Request body for the /query-selected endpoint."""
    selected_text: str = Field(..., description="User-selected text from the book")
    question: str = Field(..., description="Question about the selected text")


class QuerySelectedResponse(BaseModel):
    """Response body for the /query-selected endpoint."""
    answer: str

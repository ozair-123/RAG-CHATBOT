# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Book RAG Chatbot** system for the "AI-Driven & Spec-Driven Development Handbook" Docusaurus site powered by **Google Gemini**. Users can ask questions about book content in two modes:
1. **Global book QA**: Questions answered using RAG across the entire book
2. **Selected-text QA**: Questions answered using only user-selected text

## Development Commands

### Backend Setup & Running

```bash
# Navigate to backend
cd backend

# Install dependencies (use venv Python on Windows)
./venv/Scripts/python.exe -m pip install -r requirements.txt

# Run development server (with auto-reload)
./venv/Scripts/python.exe -m uvicorn main:app --reload --port 8000

# Alternative: Run directly
./venv/Scripts/python.exe main.py
```

### Environment Configuration

Required `.env` file in `backend/` directory:
```bash
GOOGLE_API_KEY=your_google_api_key_here
QDRANT_URL=your_qdrant_cloud_url
QDRANT_API_KEY=your_qdrant_key
```

### Testing API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Ingest book content (run once to populate vector DB)
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"docs_path": "../Ai-Spec-Driven/docs"}'

# Query with RAG
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is spec-driven development?", "top_k": 5, "mode": "answer"}'

# Query selected text
curl -X POST http://localhost:8000/query-selected \
  -H "Content-Type: application/json" \
  -d '{"selected_text": "...", "question": "What does this mean?"}'
```

## Architecture

### Component Flow

The system uses a modular RAG pipeline with clear separation of concerns:

**Startup Flow (main.py → routes.py)**
1. FastAPI initializes and calls `initialize_components()` in startup event
2. Components are initialized in order: Qdrant client → Embedder → Retriever → Ingestor → Agent
3. Qdrant collection is created/verified with correct vector dimensions
4. All components are stored as global singletons in `routes.py` for request handling

**Global RAG Query Flow (POST /query)**
1. Question → Embedder (generates embedding vector using Gemini)
2. Embedding → Retriever (searches Qdrant for top_k similar chunks)
3. Retrieved chunks + Question → BookAgent (generates answer using Gemini)
4. Returns answer + source references

**Selected Text Query Flow (POST /query-selected)**
1. Selected text + Question → BookAgent (no vector search)
2. Agent uses only provided text as context (strict mode)
3. Returns answer without sources

### Key Architectural Patterns

**Component Initialization Pattern**
- All RAG components (embedder, retriever, ingestor, agent) are initialized once at startup
- Stored as module-level globals in `api/routes.py` for efficient reuse across requests
- Avoids recreating expensive clients (Gemini, Qdrant) per request

**Sliding Window Chunking**
- Implemented in `rag/chunker.py` with configurable size/overlap
- Default: 1000 chars chunk size, 200 chars overlap, 300 chars minimum
- Metadata extraction from markdown files includes: file_path, heading, chapter, section

**Two-Phase Agent Prompting**
- Global RAG mode: Uses `GLOBAL_ANSWER_PROMPT` with formatted context chunks
- Selected text mode: Uses `SELECTED_TEXT_ANSWER_PROMPT` with strict constraints
- Mode instructions (answer/explain/summarize) dynamically append to prompts

### Directory Structure

```
backend/
├── main.py                  # FastAPI app, startup/shutdown events, CORS
├── config.py                # Pydantic settings from environment variables
├── requirements.txt         # Python dependencies (FastAPI, OpenAI, Qdrant)
├── .env                     # Environment secrets (not in git)
├── api/
│   ├── models.py            # Pydantic request/response schemas
│   └── routes.py            # API endpoints + component initialization
├── rag/
│   ├── chunker.py           # Sliding window text chunking
│   ├── embedder.py          # Google Gemini text-embedding-004 wrapper
│   ├── retriever.py         # Qdrant search with score thresholding
│   └── ingestor.py          # End-to-end ingestion pipeline
├── agents/
│   ├── agent.py             # BookAgent using Gemini with dual query methods
│   └── prompts.py           # Prompt templates for both modes
└── utils/
    ├── qdrant_client.py     # Qdrant client creation + collection setup
    └── file_loader.py       # Recursive markdown file loading
```

## RAG Configuration

**Vector Store (Qdrant Cloud)**
- Collection: `ai_spec_driven_book`
- Distance metric: Cosine
- Vector dimension: 768 (text-embedding-004)

**Retrieval Parameters**
- Default top_k: 5 chunks
- Score threshold: 0.2 (filters low-relevance results)
- Batch size for embeddings: 16

**LLM Configuration**
- Model: `gemini-1.5-flash` (configurable via `LLM_MODEL` env var)
- Embedding Model: `models/text-embedding-004`
- Temperature: 0.7
- Max tokens: 500
- Response style: 3-6 sentences, educational tone

## Key Design Constraints

- **Strict RAG mode**: Selected-text queries NEVER perform vector search; only use provided text
- **No authentication**: Hackathon/prototype mode with open endpoints
- **Markdown source**: Expects markdown files from `../Ai-Spec-Driven/docs` directory
- **CORS wide-open**: Allow all origins (restrict in production)

## Common Issues

**Google Generative AI Package**
- Requires `google-generativeai>=0.8.3`
- Ensure you have a valid Google API key with Gemini API access enabled

**Qdrant Collection Issues**
- Collection is auto-created on startup if missing
- Vector dimension mismatch will cause errors - Gemini text-embedding-004 uses 768 dimensions
- Free tier Qdrant Cloud has storage limits

**Gemini API Rate Limits**
- Free tier has rate limits on embeddings and generation
- Use batch_size parameter to control embedding request frequency

**Environment Variables**
- All config loads from `.env` file via `pydantic-settings`
- Missing API keys will cause startup failure with clear error messages

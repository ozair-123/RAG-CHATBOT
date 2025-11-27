# Book RAG Chatbot Backend

FastAPI backend for the AI-Driven & Spec-Driven Development Handbook RAG chatbot using Google Gemini.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your API keys:
   - `GOOGLE_API_KEY` - Your Google API key for Gemini
   - `QDRANT_URL` - Your Qdrant Cloud instance URL
   - `QDRANT_API_KEY` - Your Qdrant API key

3. **Run the server:**
   ```bash
   uvicorn main:app --reload --port 8000
   ```

   Or use Python directly:
   ```bash
   python main.py
   ```

## API Endpoints

### Health Check
```bash
GET /health
```

### Ingest Book
```bash
POST /ingest
Content-Type: application/json

{
  "docs_path": "../Ai-Spec-Driven/docs"
}
```

### Query Book (Global RAG)
```bash
POST /query
Content-Type: application/json

{
  "question": "What is spec-driven development?",
  "top_k": 5,
  "mode": "answer"
}
```

Modes: `answer`, `explain`, `summarize`

### Query Selected Text
```bash
POST /query-selected
Content-Type: application/json

{
  "selected_text": "Your selected text here...",
  "question": "What does this mean?"
}
```

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── config.py               # Configuration management
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── api/
│   ├── models.py           # Pydantic request/response models
│   └── routes.py           # API endpoints
├── rag/
│   ├── chunker.py          # Document chunking
│   ├── embedder.py         # Google Gemini embeddings
│   ├── retriever.py        # Qdrant vector search
│   └── ingestor.py         # Ingestion pipeline
├── agents/
│   ├── agent.py            # Google Gemini agent for answering
│   └── prompts.py          # Prompt templates
└── utils/
    ├── qdrant_client.py    # Qdrant connection
    └── file_loader.py      # Markdown file loader
```

## Usage Flow

1. Start the server
2. Call `/ingest` to load the book content into Qdrant
3. Use `/query` for global book questions
4. Use `/query-selected` for questions about specific text selections

## Configuration

All configuration is in `config.py` and can be overridden via environment variables:

- `COLLECTION_NAME` (default: "ai_spec_driven_book")
- `EMBEDDING_MODEL` (default: "models/text-embedding-004")
- `LLM_MODEL` (default: "gemini-1.5-flash")
- `CHUNK_SIZE_CHARS` (default: 1000)
- `CHUNK_OVERLAP_CHARS` (default: 200)
- `TOP_K_DEFAULT` (default: 5)
- `SCORE_THRESHOLD` (default: 0.2)

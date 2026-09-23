# Evidence-Grounded AI Chatbot Backend

Production-style Python backend for a personalized, evidence-grounded AI chatbot with local LLM generation (Ollama), ChromaDB RAG, persistent user memory, contradiction detection, and claim verification.

## Core Pipeline

```
USER QUERY
  ↓
Retrieve Validated User Memory (SQLite)
  ↓
Retrieve Document Evidence Chunks (ChromaDB)
  ↓
Build Bounded Evidence Context
  ↓
Local LLM Generation (Ollama / Grounded Fallback)
  ↓
Claim Extraction & Verification
  ↓
Assign Status: SUPPORTED / UNCERTAIN / CONFLICTING
  ↓
Return Answer + Sources + Claims + Status + Uncertainty Reason
```

## Stack

- Python 3.12+
- FastAPI & Uvicorn
- Pydantic v2
- SQLAlchemy & SQLite
- ChromaDB
- sentence-transformers (`all-MiniLM-L6-v2`)
- PyMuPDF (fitz) & python-docx
- Ollama (`llama3.2`)
- pytest & httpx

## Project Structure

```
backend/
  app.py                  # Main FastAPI application & exception handlers
  api/
    routes.py             # REST API endpoint definitions
  core/
    config.py             # Configuration & path management
    security.py           # Sanitization & input validation
  db/
    session.py            # SQLite database connection & session
    models.py             # SQLAlchemy ORM models
  ingestion/
    parsers.py            # PDF, DOCX, TXT text extractors
    chunker.py            # Overlapping chunking engine
  retrieval/
    embeddings.py         # Embedding service with SentenceTransformers & fallback
    vector_store.py       # ChromaDB PersistentClient integration
  memory/
    memory_service.py     # Memory CRUD & semantic retrieval
    conflict_service.py   # Contradiction detection & resolution
  services/
    llm_service.py        # Ollama local LLM client & grounded fallback
    orchestrator.py       # Query processing & verification pipeline
    audit_service.py      # Audit logging service
  verification/
    claim_extractor.py    # Fact claim extraction
    verifier.py           # Claim verification engine
  schemas/
    schemas.py            # Pydantic schemas for requests & responses
  tests/
    test_unit.py          # Unit tests for parsers, chunker, verifier
    test_api.py           # API endpoint tests
    test_integration.py   # Evidence grounding integration tests
  requirements.txt
  .env.example
  README.md
```

## Quick Start (Windows Setup)

### 1. Create Virtual Environment & Install Dependencies

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy `.env.example` to `.env`:

```powershell
cp .env.example .env
```

### 3. Start Ollama (Local LLM)

Ensure Ollama is installed and running:

```powershell
ollama run llama3.2
```

*(Note: If Ollama is offline or unavailable, the backend automatically uses a local grounded fallback generator).*

### 4. Run Server

```powershell
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Server API will be available at `http://localhost:8000`. Documentation is interactive at `http://localhost:8000/docs`.

### 5. Run Test Suite

```powershell
python -m pytest
```

---

## REST API Endpoints & Examples

### Health Check
`GET /health`

```bash
curl http://localhost:8000/health
```

### Upload Document
`POST /api/v1/documents`

```bash
curl -X POST http://localhost:8000/api/v1/documents \
  -F "user_id=1" \
  -F "file=@specs.pdf"
```

### Chat Request
`POST /api/v1/chat`

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "query": "What is the operating voltage of the device?"
  }'
```

### User Memory CRUD
`GET /api/v1/memory?user_id=1`
`POST /api/v1/memory`
`POST /api/v1/memory/confirm`
`DELETE /api/v1/memory/{memory_id}`

```bash
curl -X POST http://localhost:8000/api/v1/memory \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "text": "I prefer dark mode UI.",
    "type": "preference"
  }'
```

### Submit Feedback
`POST /api/v1/feedback`

```bash
curl -X POST http://localhost:8000/api/v1/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "answer_id": "ans_123",
    "label": "correct"
  }'
```

### Resolve Memory Conflict
`POST /api/v1/conflicts/{conflict_id}/resolve`

```bash
curl -X POST http://localhost:8000/api/v1/conflicts/1/resolve \
  -H "Content-Type: application/json" \
  -d '{
    "resolution": "keep_new"
  }'
```

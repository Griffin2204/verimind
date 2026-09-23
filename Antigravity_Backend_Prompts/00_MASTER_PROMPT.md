# MASTER PROMPT — Hackathon Chatbot Backend

Build a production-style but hackathon-practical Python backend for a personalized, evidence-grounded AI chatbot.

## Core pipeline
USER QUERY
→ retrieve validated user memory
→ retrieve relevant document evidence
→ build grounded context
→ local LLM generation
→ claim verification
→ SUPPORTED / UNCERTAIN / CONFLICTING response
→ explicit feedback
→ validated memory update

## Stack
- Python 3.12+
- FastAPI
- Pydantic
- SQLAlchemy
- SQLite
- ChromaDB
- sentence-transformers
- Ollama
- PyMuPDF
- python-docx
- pytest

## Browser boundary
React talks ONLY to FastAPI. Never expose SQLite, Chroma, Ollama, filesystem or model files directly to the browser.

## Required capabilities
1. Health check
2. Chat
3. Persistent memory
4. Memory CRUD
5. PDF/DOCX/TXT ingestion
6. Chunking
7. Local embeddings
8. Chroma retrieval
9. Grounded generation
10. Claim extraction
11. Verification
12. SUPPORTED / UNCERTAIN / CONFLICTING status
13. Contradiction detection
14. Conflict resolution
15. Explicit feedback/correction
16. Source/provenance retrieval
17. Audit logging
18. Validation/error handling
19. Tests

## Required endpoints
POST /api/v1/chat
POST /api/v1/documents
GET /api/v1/memory
POST /api/v1/memory/confirm
DELETE /api/v1/memory/{memory_id}
POST /api/v1/feedback
GET /api/v1/sources/{source_id}
POST /api/v1/conflicts/{conflict_id}/resolve
GET /health

## Chat rules
For every chat request:
1. Validate input.
2. Retrieve relevant validated memories.
3. Retrieve relevant document chunks.
4. Preserve provenance.
5. Build bounded evidence context.
6. Generate a draft with Ollama.
7. Extract important factual claims.
8. Verify claims against evidence.
9. Apply policy:
   - evidence supports claim → SUPPORTED
   - evidence missing/weak → UNCERTAIN
   - evidence conflicts → CONFLICTING
10. Return answer + status + claims + sources.
11. Never silently learn a permanent memory from an LLM assumption.

## Memory rules
Each memory contains:
id, user_id, text, type, source, confidence, validation_status, created_at, updated_at.

Never silently overwrite important memories. If new information conflicts with an existing memory, retain both, create a conflict, expose old/new provenance and require explicit resolution.

## RAG rules
Accept PDF, DOCX and TXT.
For every document:
- calculate hash
- extract text
- preserve page/section when possible
- chunk
- embed locally
- store vectors in Chroma
- store metadata in SQLite
- preserve document_id/page/chunk_id

Never invent citations.

## Security
Validate requests and uploads. Limit upload size. Never execute uploads. Never expose arbitrary filesystem paths or shell commands. Keep Ollama server-side. Use environment variables. Do not leak stack traces.

## Structure
backend/
  app.py
  api/
  core/
  db/
  ingestion/
  retrieval/
  verification/
  memory/
  services/
  schemas/
  tests/
  data/

## Build order
FastAPI → DB → Ollama → basic chat → memory → ingestion → embeddings/Chroma → RAG → grounded generation → verification → conflicts → feedback → provenance → tests → README.

## Deliverables
Complete source, requirements.txt, .env.example, README, tests, API examples, Windows setup commands, Ollama commands, startup commands and pytest commands.

Do not declare completion until tests pass.

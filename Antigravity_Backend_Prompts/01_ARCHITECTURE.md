# Architecture

React
↓ HTTP/JSON
FastAPI
↓
Orchestrator
├── Memory Service → SQLite
├── Document Ingestion → SQLite + Chroma
├── Retrieval → Chroma
├── LLM Service → Ollama
├── Verification → claim/NLI checks
├── Conflict Service → SQLite
└── Provenance/Audit → SQLite

The LLM is a generator, not the source of truth.

The orchestrator should maintain:
user_id, conversation_id, query, memories, retrieved_chunks, evidence_context, draft_answer, claims, verification_results, final_status, sources, uncertainty_reason and conflict.

Keep database logic out of route handlers.

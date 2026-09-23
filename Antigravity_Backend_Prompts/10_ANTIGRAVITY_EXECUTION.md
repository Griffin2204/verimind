# Antigravity Execution Instructions

Read ALL markdown files in this folder before coding.

1. Inspect the existing repository first.
2. Preserve working code.
3. Make a plan.
4. Implement incrementally.
5. Run tests after each major stage.
6. Fix failures before proceeding.
7. Keep dependencies minimal.
8. Never fake production responses.
9. Use local-first services: FastAPI, SQLite, ChromaDB, sentence-transformers and Ollama.
10. If Ollama/model is unavailable, return a clear setup error.

## Priority

P0:
FastAPI, chat, Ollama, SQLite, upload, RAG, provenance, basic verification.

P1:
memory, conflict handling, feedback.

P2:
advanced NLI, optimization, observability and optional tools.

Do not work on P2 while P0 is broken.

## Definition of done

Frontend can:
- send chat
- upload PDF
- ask questions about PDF
- receive grounded answer
- receive source metadata
- see verification status
- retrieve memory
- submit feedback

Backend:
- passes tests
- has README
- has .env.example
- has API examples
- has typed schemas
- handles common failures cleanly.

# Configuration

Create .env.example:

APP_ENV=development
DATABASE_URL=sqlite:///./data/sqlite/app.db
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=<configure-local-model>
CHROMA_PATH=./data/chroma
DOCUMENTS_PATH=./data/documents
EMBEDDING_MODEL=<configure-local-embedding-model>
MAX_UPLOAD_MB=20
TOP_K=5
SIMILARITY_THRESHOLD=0.45
CHUNK_SIZE=700
CHUNK_OVERLAP=80

Use pathlib. No hardcoded absolute paths. Do not commit .env.

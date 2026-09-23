import os
from pathlib import Path

# Base backend directory
BASE_DIR = Path(__file__).resolve().parent.parent

APP_ENV = os.getenv("APP_ENV", "development")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'data' / 'sqlite' / 'app.db'}")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

CHROMA_PATH = Path(os.getenv("CHROMA_PATH", str(BASE_DIR / "data" / "chroma")))
DOCUMENTS_PATH = Path(os.getenv("DOCUMENTS_PATH", str(BASE_DIR / "data" / "documents")))
SQLITE_DIR = Path(str(BASE_DIR / "data" / "sqlite"))

EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "20"))
TOP_K = int(os.getenv("TOP_K", "5"))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.45"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "700"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "80"))

# Ensure directories exist
def ensure_directories():
    CHROMA_PATH.mkdir(parents=True, exist_ok=True)
    DOCUMENTS_PATH.mkdir(parents=True, exist_ok=True)
    SQLITE_DIR.mkdir(parents=True, exist_ok=True)

ensure_directories()

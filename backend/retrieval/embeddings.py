import re
import requests
from typing import List
from core.config import OLLAMA_BASE_URL, OLLAMA_EMBEDDING_MODEL

# ngrok's free tier shows an interstitial warning page to any request
# without this header, which would otherwise break embedding calls
# the same way it broke chat calls in llm_service.py.
NGROK_HEADERS = {"ngrok-skip-browser-warning": "true"}


class EmbeddingService:
    """
    Calls Ollama's /api/embeddings endpoint instead of loading a local
    sentence-transformers model. This removes the sentence-transformers
    -> Torch dependency chain from this process entirely, which was the
    largest single contributor to out-of-memory crashes on Render's
    512MB free tier. Falls back to a deterministic pseudo-embedding if
    Ollama is unreachable, so ingestion/search never hard-fail.
    """

    def __init__(self, model_name: str = OLLAMA_EMBEDDING_MODEL):
        self.model_name = model_name
        self.base_url = OLLAMA_BASE_URL.rstrip("/")

    def _embed_one(self, text: str):
        try:
            res = requests.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.model_name, "prompt": text},
                headers=NGROK_HEADERS,
                timeout=15.0
            )
            if res.status_code == 200:
                data = res.json()
                embedding = data.get("embedding")
                if embedding:
                    return embedding
        except Exception as e:
            print(f"[EmbeddingService] Ollama embedding failed or offline ({e}). Using fallback embedding.")

        return self._fallback_embedding(text)

    # Must match nomic-embed-text's output dimensionality (768) so a
    # fallback embedding never mismatches real Ollama embeddings that
    # already exist in the same Chroma collection. If you change
    # OLLAMA_EMBEDDING_MODEL to a model with a different embedding
    # size, update this to match.
    FALLBACK_DIM = 768

    def _fallback_embedding(self, text: str) -> List[float]:
        # Deterministic pseudo-embedding vector, used only if
        # Ollama/the ngrok tunnel is unreachable.
        words = re.findall(r'\w+', text.lower())
        vec = [0.0] * self.FALLBACK_DIM
        for idx, w in enumerate(words[:self.FALLBACK_DIM]):
            hash_val = sum(ord(c) for c in w)
            vec[idx % self.FALLBACK_DIM] += (hash_val % 100) / 100.0
        norm = sum(x * x for x in vec) ** 0.5 or 1.0
        return [x / norm for x in vec]

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        return [self._embed_one(t) for t in texts]

    def embed_query(self, query: str) -> List[float]:
        return self.embed_texts([query])[0]


embedding_service = EmbeddingService()
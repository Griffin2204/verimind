import re
from typing import List
from core.config import EMBEDDING_MODEL_NAME

class EmbeddingService:
    def __init__(self, model_name: str = EMBEDDING_MODEL_NAME):
        self.model_name = model_name
        self._model = None

    def _get_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
            except Exception as e:
                print(f"[EmbeddingService] Warning: Could not load SentenceTransformer ({e}). Using fallback embedding.")
                self._model = "fallback"
        return self._model

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        model = self._get_model()
        if model != "fallback":
            embeddings = model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
        else:
            # Fallback deterministic pseudo-embedding vector of 384 dimensions
            results = []
            for t in texts:
                words = re.findall(r'\w+', t.lower())
                vec = [0.0] * 384
                for idx, w in enumerate(words[:384]):
                    hash_val = sum(ord(c) for c in w)
                    vec[idx % 384] += (hash_val % 100) / 100.0
                norm = sum(x*x for x in vec) ** 0.5 or 1.0
                results.append([x / norm for x in vec])
            return results

    def embed_query(self, query: str) -> List[float]:
        return self.embed_texts([query])[0]

embedding_service = EmbeddingService()

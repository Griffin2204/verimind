import chromadb
from typing import List, Dict, Any, Optional
from core.config import CHROMA_PATH, TOP_K, SIMILARITY_THRESHOLD
from retrieval.embeddings import embedding_service

class VectorStoreService:
    def __init__(self, collection_name: str = "document_chunks"):
        self.chroma_client = chromadb.PersistentClient(path=str(CHROMA_PATH))
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, chunks: List[Any], filename: str, user_id: int = 1):
        if not chunks:
            return
            
        ids = [c.chunk_id for c in chunks]
        texts = [c.text for c in chunks]
        metadatas = [
            {
                "user_id": int(user_id),
                "document_id": int(c.document_id),
                "chunk_id": str(c.chunk_id),
                "filename": str(filename),
                "page": int(c.page) if c.page else 1,
                "section": str(c.section) if c.section else "General"
            }
            for c in chunks
        ]
        
        embeddings = embedding_service.embed_texts(texts)
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )

    def search(
        self,
        query: str,
        user_doc_ids: Optional[List[int]] = None,
        top_k: int = TOP_K,
        similarity_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        query_embedding = embedding_service.embed_query(query)
        
        count = self.collection.count()
        if count == 0:
            return []
            
        n_search = max(20, top_k * 4)
        actual_n = min(n_search, count)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=actual_n,
            include=["documents", "metadatas", "distances"]
        )
        
        valid_doc_set = set(int(x) for x in user_doc_ids) if user_doc_ids is not None else None

        retrieved_by_doc: Dict[int, List[Dict[str, Any]]] = {}
        if results and results.get("ids") and results["ids"][0]:
            ids = results["ids"][0]
            docs = results["documents"][0]
            metadatas = results["metadatas"][0]
            distances = results["distances"][0]
            
            for chunk_id, doc_text, meta, dist in zip(ids, docs, metadatas, distances):
                try:
                    doc_id = int(meta.get("document_id", 0))
                except (ValueError, TypeError):
                    doc_id = 0
                
                # Filter by user document ownership if provided
                if valid_doc_set is not None and doc_id not in valid_doc_set:
                    continue
                    
                similarity = 1.0 - float(dist)
                if similarity >= similarity_threshold:
                    item = {
                        "source_id": f"src_{doc_id}_{chunk_id}",
                        "document_id": doc_id,
                        "filename": meta.get("filename", "document"),
                        "page": meta.get("page", 1),
                        "section": meta.get("section", "General"),
                        "chunk_id": chunk_id,
                        "snippet": doc_text,
                        "similarity": similarity
                    }
                    if doc_id not in retrieved_by_doc:
                        retrieved_by_doc[doc_id] = []
                    retrieved_by_doc[doc_id].append(item)
                    
        # Interleave top candidate chunks from different documents of the user
        retrieved_items = []
        doc_ids = list(retrieved_by_doc.keys())
        max_chunks_per_doc = max(1, (top_k + len(doc_ids) - 1) // len(doc_ids)) if doc_ids else 1
        
        for doc_id in doc_ids:
            retrieved_items.extend(retrieved_by_doc[doc_id][:max_chunks_per_doc])
            
        retrieved_items.sort(key=lambda x: x["similarity"], reverse=True)
        return retrieved_items

    def delete_document_chunks(self, document_id: int):
        try:
            self.collection.delete(where={"document_id": int(document_id)})
        except Exception as e:
            print(f"[VectorStoreService] Error deleting chunks for document {document_id}: {e}")

vector_store_service = VectorStoreService()

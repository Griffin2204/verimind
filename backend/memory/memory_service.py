from sqlalchemy.orm import Session
from typing import List, Optional
import datetime
from db.models import Memory
from retrieval.embeddings import embedding_service

def get_validated_memories(db: Session, user_id: int, query: Optional[str] = None) -> List[Memory]:
    query_builder = db.query(Memory).filter(
        Memory.user_id == user_id,
        Memory.validation_status == "validated"
    )
    all_memories = query_builder.all()
    if not query or not all_memories:
        return all_memories
        
    # Semantic relevance filtering for user query
    query_emb = embedding_service.embed_query(query)
    memories_with_sim = []
    for mem in all_memories:
        mem_emb = embedding_service.embed_query(mem.text)
        sim = sum(a * b for a, b in zip(query_emb, mem_emb))
        if sim >= 0.3:
            memories_with_sim.append((mem, sim))
            
    memories_with_sim.sort(key=lambda x: x[1], reverse=True)
    return [m[0] for m in memories_with_sim] if memories_with_sim else all_memories

def create_memory(db: Session, user_id: int, text: str, memory_type: str = "fact", source: str = "user", confidence: float = 1.0, validation_status: str = "validated") -> Memory:
    memory = Memory(
        user_id=user_id,
        text=text,
        type=memory_type,
        source=source,
        confidence=confidence,
        validation_status=validation_status,
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow()
    )
    db.add(memory)
    db.commit()
    db.refresh(memory)
    return memory

def confirm_memory(db: Session, memory_id: int) -> Optional[Memory]:
    memory = db.query(Memory).filter(Memory.id == memory_id).first()
    if memory:
        memory.validation_status = "validated"
        memory.updated_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(memory)
    return memory

def delete_memory(db: Session, memory_id: int) -> bool:
    memory = db.query(Memory).filter(Memory.id == memory_id).first()
    if memory:
        db.delete(memory)
        db.commit()
        return True
    return False

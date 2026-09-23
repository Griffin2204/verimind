from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
import datetime
from db.models import Memory, Conflict
from retrieval.embeddings import embedding_service
from memory.memory_service import create_memory

def check_memory_conflict(existing_memories: List[Memory], new_text: str) -> Optional[Memory]:
    if not existing_memories:
        return None
        
    new_emb = embedding_service.embed_query(new_text)
    new_text_lower = new_text.lower()
    
    for mem in existing_memories:
        mem_emb = embedding_service.embed_query(mem.text)
        sim = sum(a * b for a, b in zip(new_emb, mem_emb))
        
        # High semantic similarity but non-identical text suggests conflicting statement
        if sim > 0.65 and mem.text.lower() != new_text_lower:
            return mem
            
        # Keyword conflict checks (e.g., preference shifts)
        if "prefer" in new_text_lower and "prefer" in mem.text.lower():
            if mem.text.lower() != new_text_lower:
                return mem
                
    return None

def add_memory_with_conflict_check(db: Session, user_id: int, text: str, memory_type: str = "fact", source: str = "user", confidence: float = 1.0) -> Tuple[Memory, Optional[Conflict]]:
    existing_memories = db.query(Memory).filter(
        Memory.user_id == user_id,
        Memory.validation_status == "validated"
    ).all()
    
    conflicting_mem = check_memory_conflict(existing_memories, text)
    
    if conflicting_mem:
        # Create new memory with 'pending' validation status until conflict is resolved
        new_mem = create_memory(
            db, user_id=user_id, text=text, memory_type=memory_type,
            source=source, confidence=confidence, validation_status="pending"
        )
        conflict = Conflict(
            old_memory_id=conflicting_mem.id,
            new_memory_id=new_mem.id,
            status="pending",
            created_at=datetime.datetime.utcnow()
        )
        db.add(conflict)
        db.commit()
        db.refresh(conflict)
        return new_mem, conflict
    else:
        new_mem = create_memory(
            db, user_id=user_id, text=text, memory_type=memory_type,
            source=source, confidence=confidence, validation_status="validated"
        )
        return new_mem, None

def resolve_conflict(db: Session, conflict_id: int, resolution: str) -> Tuple[bool, Optional[Conflict]]:
    conflict = db.query(Conflict).filter(Conflict.id == conflict_id).first()
    if not conflict:
        return False, None
        
    old_mem = db.query(Memory).filter(Memory.id == conflict.old_memory_id).first()
    new_mem = db.query(Memory).filter(Memory.id == conflict.new_memory_id).first()
    
    if resolution == "keep_old":
        if old_mem: old_mem.validation_status = "validated"
        if new_mem: new_mem.validation_status = "superseded"
    elif resolution == "keep_new":
        if old_mem: old_mem.validation_status = "superseded"
        if new_mem: new_mem.validation_status = "validated"
    elif resolution == "keep_both":
        if old_mem: old_mem.validation_status = "validated"
        if new_mem: new_mem.validation_status = "validated"
    else:
        raise ValueError(f"Invalid resolution type: {resolution}")
        
    conflict.status = "resolved"
    conflict.resolution = resolution
    conflict.resolved_at = datetime.datetime.utcnow()
    
    db.commit()
    db.refresh(conflict)
    return True, conflict

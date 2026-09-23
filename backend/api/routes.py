import hashlib
import datetime
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from sqlalchemy import text
from db.session import get_db
from db.models import User, Memory, Document, Chunk, Feedback, Conflict
from schemas.schemas import (
    HealthResponse, ChatRequest, ChatResponse, DocumentUploadResponse,
    MemoryItem, MemoryCreateRequest, MemoryConfirmRequest,
    FeedbackRequest, FeedbackResponse, SourceDetailResponse,
    ConflictResolveRequest, ConflictResolveResponse, ConflictItem,
    ErrorResponse
)
from core.config import MAX_UPLOAD_MB, DOCUMENTS_PATH
from core.security import sanitize_filename, validate_extension
from ingestion.parsers import parse_document
from ingestion.chunker import chunk_document
from retrieval.vector_store import vector_store_service
from memory.memory_service import (
    get_validated_memories, create_memory, confirm_memory, delete_memory
)
from memory.conflict_service import add_memory_with_conflict_check, resolve_conflict
from services.orchestrator import process_chat_query
from services.llm_service import llm_service
from services.audit_service import log_audit_event

router = APIRouter()

# Helper function to get or create default user
def get_or_create_user(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        user = User(id=user_id, name=f"User {user_id}", created_at=datetime.datetime.utcnow())
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

# Health check endpoint
@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"

    chroma_status = "healthy"
    try:
        vector_store_service.collection.count()
    except Exception:
        chroma_status = "unhealthy"

    ollama_status = llm_service.check_health()

    return HealthResponse(
        status="ok" if db_status == "healthy" and chroma_status == "healthy" else "degraded",
        services={
            "database": db_status,
            "vector_store": chroma_status,
            "ollama": ollama_status
        }
    )

# POST /api/v1/chat
@router.post("/api/v1/chat", response_model=ChatResponse)
def chat_endpoint(payload: ChatRequest, db: Session = Depends(get_db)):
    if not payload.query or not payload.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "INVALID_QUERY", "message": "Query string cannot be empty."}}
        )
        
    get_or_create_user(db, payload.user_id)
    return process_chat_query(
        db=db,
        user_id=payload.user_id,
        query=payload.query.strip(),
        conversation_id=payload.conversation_id
    )

# POST /api/v1/documents
@router.post("/api/v1/documents", response_model=DocumentUploadResponse)
async def upload_document(
    user_id: int = Form(1),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    get_or_create_user(db, user_id)
    
    filename = sanitize_filename(file.filename or "document.txt")
    if not validate_extension(filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "INVALID_FILE_TYPE", "message": "Only PDF, DOCX, and TXT files are allowed."}}
        )

    content = await file.read()
    if len(content) > MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "FILE_TOO_LARGE", "message": f"File size exceeds maximum limit of {MAX_UPLOAD_MB}MB."}}
        )

    file_hash = hashlib.sha256(content).hexdigest()

    # Check for existing document with same hash for user
    existing_doc = db.query(Document).filter(Document.user_id == user_id, Document.file_hash == file_hash).first()
    if existing_doc:
        chunk_count = db.query(Chunk).filter(Chunk.document_id == existing_doc.id).count()
        return DocumentUploadResponse(
            document_id=existing_doc.id,
            filename=existing_doc.filename,
            file_hash=existing_doc.file_hash,
            status="processed",
            chunk_count=chunk_count
        )

    # Save to filesystem
    file_path = DOCUMENTS_PATH / f"{file_hash}_{filename}"
    with open(file_path, "wb") as f:
        f.write(content)

    # Parse text
    try:
        parsed_sections = parse_document(filename, content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "PARSE_ERROR", "message": f"Could not parse file content: {str(e)}"}}
        )

    # Create Document record
    doc_record = Document(
        user_id=user_id,
        filename=filename,
        file_hash=file_hash,
        uploaded_at=datetime.datetime.utcnow()
    )
    db.add(doc_record)
    db.commit()
    db.refresh(doc_record)

    # Chunk text
    chunks_dto = chunk_document(doc_record.id, parsed_sections)

    # Add to SQLite
    for c in chunks_dto:
        chunk_rec = Chunk(
            id=c.chunk_id,
            document_id=doc_record.id,
            page=c.page,
            section=c.section,
            text=c.text,
            created_at=datetime.datetime.utcnow()
        )
        db.add(chunk_rec)
    db.commit()

    # Embed and add to Chroma
    vector_store_service.add_chunks(chunks_dto, filename=filename, user_id=user_id)

    log_audit_event(
        db, event_name="document_upload", user_id=user_id,
        metadata={"document_id": doc_record.id, "filename": filename, "chunks": len(chunks_dto)}
    )

    return DocumentUploadResponse(
        document_id=doc_record.id,
        filename=filename,
        file_hash=file_hash,
        status="processed",
        chunk_count=len(chunks_dto)
    )

# GET /api/v1/memory?user_id=1
@router.get("/api/v1/memory", response_model=List[MemoryItem])
def get_memories(user_id: int = 1, db: Session = Depends(get_db)):
    memories = db.query(Memory).filter(Memory.user_id == user_id).all()
    return memories

# POST /api/v1/memory
@router.post("/api/v1/memory", response_model=MemoryItem)
def add_memory(payload: MemoryCreateRequest, db: Session = Depends(get_db)):
    get_or_create_user(db, payload.user_id)
    mem, conflict = add_memory_with_conflict_check(
        db, user_id=payload.user_id, text=payload.text,
        memory_type=payload.type, source=payload.source, confidence=payload.confidence
    )
    return mem

# POST /api/v1/memory/confirm
@router.post("/api/v1/memory/confirm", response_model=MemoryItem)
def confirm_memory_endpoint(payload: MemoryConfirmRequest, db: Session = Depends(get_db)):
    mem = confirm_memory(db, payload.memory_id)
    if not mem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "MEMORY_NOT_FOUND", "message": "Memory record not found."}}
        )
    return mem

# DELETE /api/v1/memory/{memory_id}
@router.delete("/api/v1/memory/{memory_id}")
def delete_memory_endpoint(memory_id: int, db: Session = Depends(get_db)):
    success = delete_memory(db, memory_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "MEMORY_NOT_FOUND", "message": "Memory record not found."}}
        )
    return {"status": "deleted", "memory_id": memory_id}

# POST /api/v1/feedback
@router.post("/api/v1/feedback", response_model=FeedbackResponse)
def submit_feedback(payload: FeedbackRequest, db: Session = Depends(get_db)):
    get_or_create_user(db, payload.user_id)
    allowed_labels = {"correct", "incorrect", "not_enough_evidence", "correction"}
    if payload.label not in allowed_labels:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "INVALID_LABEL", "message": f"Label must be one of {allowed_labels}"}}
        )

    fb = Feedback(
        user_id=payload.user_id,
        answer_id=payload.answer_id,
        query=payload.query,
        answer=payload.answer,
        label=payload.label,
        correction=payload.correction,
        created_at=datetime.datetime.utcnow()
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)

    # If feedback is an explicit correction, add as a candidate memory with conflict check
    if payload.label == "correction" and payload.correction:
        add_memory_with_conflict_check(
            db, user_id=payload.user_id, text=payload.correction,
            memory_type="correction", source="user_feedback"
        )

    log_audit_event(db, event_name="feedback_submitted", user_id=payload.user_id, metadata={"label": payload.label})

    return FeedbackResponse(id=fb.id, status="received")

# GET /api/v1/sources/{source_id}
@router.get("/api/v1/sources/{source_id}", response_model=SourceDetailResponse)
def get_source_detail(source_id: str, db: Session = Depends(get_db)):
    # source_id format: src_{doc_id}_{chunk_id} or direct chunk_id
    chunk = db.query(Chunk).filter(Chunk.id.endswith(source_id.split("_")[-1])).first()
    if not chunk:
        chunk = db.query(Chunk).filter(Chunk.id == source_id).first()
        
    if not chunk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "SOURCE_NOT_FOUND", "message": "Source details not found."}}
        )

    doc = db.query(Document).filter(Document.id == chunk.document_id).first()
    filename = doc.filename if doc else "Unknown"

    return SourceDetailResponse(
        source_id=source_id,
        document_id=chunk.document_id,
        filename=filename,
        page=chunk.page,
        section=chunk.section,
        chunk_id=chunk.id,
        snippet=chunk.text
    )

# GET /api/v1/conflicts
@router.get("/api/v1/conflicts", response_model=List[ConflictItem])
def get_conflicts(db: Session = Depends(get_db)):
    return db.query(Conflict).all()

# POST /api/v1/conflicts/{conflict_id}/resolve
@router.post("/api/v1/conflicts/{conflict_id}/resolve", response_model=ConflictResolveResponse)
def resolve_conflict_endpoint(conflict_id: int, payload: ConflictResolveRequest, db: Session = Depends(get_db)):
    allowed_resolutions = {"keep_old", "keep_new", "keep_both"}
    if payload.resolution not in allowed_resolutions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "INVALID_RESOLUTION", "message": f"Resolution must be one of {allowed_resolutions}"}}
        )

    try:
        success, conflict = resolve_conflict(db, conflict_id, payload.resolution)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "INVALID_RESOLUTION", "message": str(e)}}
        )

    if not success or not conflict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "CONFLICT_NOT_FOUND", "message": "Conflict record not found."}}
        )

    return ConflictResolveResponse(
        conflict_id=conflict.id,
        status=conflict.status,
        resolution=conflict.resolution
    )

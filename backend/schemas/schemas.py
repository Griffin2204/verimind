from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict
import datetime

class HealthResponse(BaseModel):
    status: str
    services: Dict[str, str]

class ChatRequest(BaseModel):
    user_id: int = 1
    query: str
    conversation_id: Optional[str] = None

class SourceItem(BaseModel):
    source_id: str
    document_id: int
    filename: str
    page: Optional[int] = None
    chunk_id: str
    snippet: str

class ClaimItem(BaseModel):
    text: str
    status: str # SUPPORTED, UNCERTAIN, CONFLICTING
    confidence: float
    source_ids: List[str] = []
    contradiction_source_ids: List[str] = []

class ChatResponse(BaseModel):
    answer: str
    status: str # SUPPORTED, UNCERTAIN, CONFLICTING
    sources: List[SourceItem] = []
    claims: List[ClaimItem] = []
    uncertainty_reason: Optional[str] = None

class DocumentUploadResponse(BaseModel):
    document_id: int
    filename: str
    file_hash: str
    status: str
    chunk_count: int

class MemoryCreateRequest(BaseModel):
    user_id: int = 1
    text: str
    type: str = "fact"
    source: str = "user"
    confidence: float = 1.0

class MemoryItem(BaseModel):
    id: int
    user_id: int
    text: str
    type: str
    source: str
    confidence: float
    validation_status: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class MemoryConfirmRequest(BaseModel):
    memory_id: int

class FeedbackRequest(BaseModel):
    user_id: int = 1
    answer_id: str
    query: Optional[str] = None
    answer: Optional[str] = None
    label: str # correct, incorrect, not_enough_evidence, correction
    correction: Optional[str] = None

class FeedbackResponse(BaseModel):
    id: int
    status: str

class SourceDetailResponse(BaseModel):
    source_id: str
    document_id: int
    filename: str
    page: Optional[int] = None
    section: Optional[str] = None
    chunk_id: str
    snippet: str

class ConflictResolveRequest(BaseModel):
    resolution: str # keep_old, keep_new, keep_both

class ConflictResolveResponse(BaseModel):
    conflict_id: int
    status: str
    resolution: str

class ConflictItem(BaseModel):
    id: int
    old_memory_id: int
    new_memory_id: int
    status: str
    resolution: Optional[str] = None
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class ErrorDetail(BaseModel):
    code: str
    message: str

class ErrorResponse(BaseModel):
    error: ErrorDetail

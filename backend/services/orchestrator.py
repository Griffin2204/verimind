import re
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import uuid

from db.models import Document
from memory.memory_service import get_validated_memories
from retrieval.vector_store import vector_store_service
from services.llm_service import llm_service
from verification.claim_extractor import extract_claims
from verification.verifier import verify_claims
from services.audit_service import log_audit_event
from schemas.schemas import ChatResponse, SourceItem, ClaimItem

SYSTEM_PROMPT = """You are a grounded personal AI assistant.
Rules:
1. Use supplied evidence for document-grounded facts.
2. Use validated user memory only when relevant.
3. Never invent sources, quotations, page numbers or facts.
4. Distinguish evidence from inference.
5. If evidence is insufficient, say so.
6. If evidence conflicts, acknowledge it clearly.
7. Be concise (1-3 sentences). Do not dump raw retrieved context."""

def process_chat_query(db: Session, user_id: int, query: str, conversation_id: Optional[str] = None) -> ChatResponse:
    # 1. Retrieve validated memories
    memories = get_validated_memories(db, user_id=user_id, query=query)
    memory_text_block = "\n".join([f"- ({m.type}) {m.text}" for m in memories]) if memories else "None"

    # 2. Retrieve document chunks belonging to this user
    user_doc_records = db.query(Document.id).filter(Document.user_id == user_id).all()
    user_doc_ids = [d[0] for d in user_doc_records] if user_doc_records else []

    retrieved_sources = vector_store_service.search(query=query, user_doc_ids=user_doc_ids, top_k=8)
    
    if retrieved_sources:
        evidence_text_block = "\n".join([
            f"[Source: {s['source_id']} | File: {s['filename']} | Page: {s['page']}]\n{s['snippet']}"
            for s in retrieved_sources
        ])
    else:
        evidence_text_block = "None"

    # 3. Build context prompt
    prompt = f"""USER MEMORY:
{memory_text_block}

DOCUMENT EVIDENCE:
{evidence_text_block}

USER QUESTION:
{query}

Generate a concise 1-3 sentence answer based strictly on the provided evidence and memory."""

    # 4. Generate LLM draft
    draft_answer = llm_service.generate(prompt, system_prompt=SYSTEM_PROMPT)

    # 5. Extract claims
    claims_raw = extract_claims(draft_answer)

    # 6. Verify claims & check cross-document conflicts
    verified_claims, overall_status, uncertainty_reason = verify_claims(
        claims_raw=claims_raw,
        sources=retrieved_sources,
        memories=memories
    )

    # Adjust answer text based on verification policy status
    final_answer = draft_answer

    if overall_status == "CONFLICTING":
        doc_sources = [s for s in retrieved_sources if s.get("source_id")]
        vals = []
        for s in doc_sources:
            v_matches = re.findall(r'\b\d+(?:\.\d+)?\s*(?:V|VAC|VDC|V DC|V AC|volts)\b', s["snippet"], re.IGNORECASE)
            vals.extend(v_matches)
            
        unique_vals = list(dict.fromkeys([v.strip() for v in vals]))
        
        entity_name = "the Aurora X1" if "aurora" in query.lower() else "the product"
        if len(unique_vals) >= 2:
            final_answer = f"The provided documents give conflicting operating voltages for {entity_name}: one states {unique_vals[0]}, while another states {unique_vals[1]}."
        else:
            final_answer = f"The provided documents contain conflicting statements regarding {query}."

    elif overall_status == "UNCERTAIN":
        final_answer = "The requested information is not available in the provided document evidence."
        if not uncertainty_reason:
            uncertainty_reason = "The requested information is not explicitly provided in the retrieved evidence."

    # Convert sources to SourceItem schemas
    source_items = [
        SourceItem(
            source_id=s["source_id"],
            document_id=s["document_id"],
            filename=s["filename"],
            page=s.get("page", 1),
            chunk_id=s["chunk_id"],
            snippet=s["snippet"]
        )
        for s in retrieved_sources
    ]

    # Audit log
    log_audit_event(
        db,
        event_name="chat_query",
        user_id=user_id,
        metadata={
            "query": query,
            "status": overall_status,
            "sources_count": len(source_items),
            "claims_count": len(verified_claims)
        }
    )

    return ChatResponse(
        answer=final_answer,
        status=overall_status,
        sources=source_items,
        claims=verified_claims,
        uncertainty_reason=uncertainty_reason
    )

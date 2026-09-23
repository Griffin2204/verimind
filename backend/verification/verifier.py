import re
from typing import List, Dict, Any, Tuple, Optional
from retrieval.embeddings import embedding_service
from schemas.schemas import ClaimItem, SourceItem

STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "and", "or", "in", "on", "at",
    "to", "for", "of", "with", "it", "this", "that", "be", "by", "from", "as",
    "has", "have", "had", "does", "do", "did", "can", "could", "should", "would"
}

NON_ENTITY_WORDS = {
    "V", "DC", "AC", "VAC", "VDC", "W", "HZ", "KG", "G", "M", "CM", "MM",
    "GB", "TB", "MB", "USD", "EUR", "INR", "DOC", "DOCUMENT", "PAGE", "THE",
    "THIS", "THAT", "SPECIFICATIONS", "SPEC", "TEST", "RAG", "BACKEND"
}

def calculate_overlap_ratio(text1: str, text2: str) -> float:
    words1 = set(re.findall(r'\w+', text1.lower())) - STOP_WORDS
    words2 = set(re.findall(r'\w+', text2.lower())) - STOP_WORDS
    if not words1 or not words2:
        return 0.0
    common = words1.intersection(words2)
    return len(common) / min(len(words1), len(words2))

def extract_values_and_units(text: str) -> List[str]:
    patterns = [
        r'\b\d+(?:\.\d+)?\s*(?:V|VAC|VDC|V DC|V AC|W|Hz|kW|MHz|GHz|kg|g|m|cm|mm|GB|TB|MB|USD|\$|EUR|INR|rupees|dollars)\b',
        r'\b\$\d+(?:\.\d+)?\b'
    ]
    found = []
    for pat in patterns:
        matches = re.findall(pat, text, re.IGNORECASE)
        found.extend([m.strip() for m in matches])
    return found

def extract_entities(text: str) -> set:
    words = set(re.findall(r'\b[A-Z][A-Za-z0-9_]+\b', text))
    clean_entities = set()
    for w in words:
        if w.upper() not in NON_ENTITY_WORDS and len(w) > 1:
            clean_entities.add(w)
    return clean_entities

def detect_cross_document_conflict(sources: List[Dict[str, Any]]) -> Tuple[bool, List[str], List[str]]:
    if not sources or len(sources) < 2:
        return False, [], []

    # Group sources by document_id
    by_doc: Dict[int, List[Dict[str, Any]]] = {}
    for s in sources:
        doc_id = s["document_id"]
        if doc_id not in by_doc:
            by_doc[doc_id] = []
        by_doc[doc_id].append(s)

    if len(by_doc) < 2:
        return False, [], []

    doc_ids = list(by_doc.keys())
    conflicting_source_ids = set()
    conflict_details = []

    # Check pairwise between documents
    for i in range(len(doc_ids)):
        for j in range(i + 1, len(doc_ids)):
            doc1_id = doc_ids[i]
            doc2_id = doc_ids[j]

            for s1 in by_doc[doc1_id]:
                text1 = s1["snippet"]
                vals1 = extract_values_and_units(text1)
                entities1 = extract_entities(text1)

                for s2 in by_doc[doc2_id]:
                    text2 = s2["snippet"]
                    vals2 = extract_values_and_units(text2)
                    entities2 = extract_entities(text2)

                    common_entities = entities1.intersection(entities2)

                    if common_entities and vals1 and vals2:
                        set1 = set([v.lower() for v in vals1])
                        set2 = set([v.lower() for v in vals2])
                        if not set1.intersection(set2) and set1 != set2:
                            conflicting_source_ids.add(s1["source_id"])
                            conflicting_source_ids.add(s2["source_id"])
                            conflict_details.append(f"Doc {doc1_id} ({s1['filename']}): {vals1[0]} vs Doc {doc2_id} ({s2['filename']}): {vals2[0]}")

    if conflicting_source_ids:
        return True, list(conflicting_source_ids), conflict_details

    return False, [], []

def verify_claims(
    claims_raw: List[Dict[str, str]],
    sources: List[Dict[str, Any]],
    memories: List[Any]
) -> Tuple[List[ClaimItem], str, Optional[str]]:

    # 1. Check cross-document conflict
    is_conflict, conflict_src_ids, conflict_details = detect_cross_document_conflict(sources)

    if not claims_raw:
        if is_conflict:
            return [], "CONFLICTING", f"Conflicting evidence detected across documents: {'; '.join(conflict_details)}"
        return [], "UNCERTAIN", "No specific factual claims were generated."

    if not sources and not memories:
        verified_claims = [
            ClaimItem(
                text=c["text"],
                status="UNCERTAIN",
                confidence=0.0,
                source_ids=[]
            )
            for c in claims_raw
        ]
        return verified_claims, "UNCERTAIN", "Insufficient document evidence or user memory retrieved to ground claims."

    verified_claims = []
    has_supported = False
    has_uncertain = False

    for c in claims_raw:
        claim_text = c["text"]
        claim_emb = embedding_service.embed_query(claim_text)
        
        matched_source_ids = []
        max_sim = 0.0
        
        # Check against document sources
        for src in sources:
            src_emb = embedding_service.embed_query(src["snippet"])
            sim = sum(a * b for a, b in zip(claim_emb, src_emb))
            overlap = calculate_overlap_ratio(claim_text, src["snippet"])
            
            combined_score = max(sim, overlap)
            if combined_score >= 0.40:
                matched_source_ids.append(src["source_id"])
                if combined_score > max_sim:
                    max_sim = combined_score
                    
        # Check against memories
        for mem in memories:
            mem_emb = embedding_service.embed_query(mem.text)
            sim = sum(a * b for a, b in zip(claim_emb, mem_emb))
            overlap = calculate_overlap_ratio(claim_text, mem.text)
            combined_score = max(sim, overlap)
            if combined_score >= 0.40:
                matched_source_ids.append(f"mem_{mem.id}")
                if combined_score > max_sim:
                    max_sim = combined_score

        if is_conflict:
            claim_status = "CONFLICTING"
            confidence = 0.50
        elif matched_source_ids:
            claim_status = "SUPPORTED"
            confidence = min(0.95, round(max_sim, 2))
            has_supported = True
        else:
            claim_status = "UNCERTAIN"
            confidence = 0.30
            has_uncertain = True

        verified_claims.append(
            ClaimItem(
                text=claim_text,
                status=claim_status,
                confidence=confidence,
                source_ids=matched_source_ids,
                contradiction_source_ids=conflict_src_ids if is_conflict else []
            )
        )

    if is_conflict:
        overall_status = "CONFLICTING"
        uncertainty_reason = f"Conflicting evidence detected across retrieved documents: {'; '.join(conflict_details)}"
    elif has_supported:
        overall_status = "SUPPORTED"
        uncertainty_reason = None
    else:
        overall_status = "UNCERTAIN"
        uncertainty_reason = "The requested information is not explicitly provided in the retrieved evidence."

    return verified_claims, overall_status, uncertainty_reason

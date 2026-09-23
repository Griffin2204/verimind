import pytest
from ingestion.parsers import parse_txt, parse_document
from ingestion.chunker import chunk_document
from retrieval.embeddings import embedding_service
from verification.verifier import verify_claims
from verification.claim_extractor import extract_claims

def test_txt_parsing():
    content = b"Line 1: Hello World.\nLine 2: Test parsing."
    sections = parse_txt(content)
    assert len(sections) == 1
    assert "Hello World" in sections[0]["text"]

def test_unsupported_file_rejection():
    with pytest.raises(ValueError, match="Unsupported file format"):
        parse_document("test.exe", b"binary content")

def test_chunking():
    parsed_sections = [{"page": 1, "section": "Intro", "text": "Short snippet."}]
    chunks = chunk_document(document_id=1, parsed_sections=parsed_sections, chunk_size=100, chunk_overlap=20)
    assert len(chunks) == 1
    assert chunks[0].document_id == 1
    assert chunks[0].chunk_id == "doc_1_chunk_0"
    assert chunks[0].text == "Short snippet."

def test_embedding_service():
    texts = ["Testing sentence transformers", "Another sentence"]
    embeddings = embedding_service.embed_texts(texts)
    assert len(embeddings) == 2
    assert len(embeddings[0]) > 0

def test_claim_extraction():
    answer = "The device operates at 230 V AC. It is painted blue."
    claims = extract_claims(answer)
    assert len(claims) == 2
    assert claims[0]["text"] == "The device operates at 230 V AC."

def test_verification_policy_supported():
    claims = [{"text": "The device operates at 230 V AC."}]
    sources = [{
        "source_id": "src_1",
        "document_id": 1,
        "filename": "test.txt",
        "page": 1,
        "chunk_id": "chunk_0",
        "snippet": "The device operates at 230 V AC and 50 Hz."
    }]
    verified, status, reason = verify_claims(claims, sources, memories=[])
    assert status == "SUPPORTED"
    assert verified[0].status == "SUPPORTED"
    assert "src_1" in verified[0].source_ids

def test_verification_policy_uncertain():
    claims = [{"text": "The device costs 500 dollars."}]
    sources = [{
        "source_id": "src_1",
        "document_id": 1,
        "filename": "test.txt",
        "page": 1,
        "chunk_id": "chunk_0",
        "snippet": "The device operates at 230 V AC and 50 Hz."
    }]
    verified, status, reason = verify_claims(claims, sources, memories=[])
    assert status == "UNCERTAIN"
    assert verified[0].status == "UNCERTAIN"
    assert reason is not None

import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_evidence_grounding_integration():
    # 1. Seed document
    doc_content = b"The device operates at 230 V AC and 50 Hz. The enclosure rating is IP65."
    upload_res = client.post(
        "/api/v1/documents",
        data={"user_id": 100},
        files={"file": ("device_specs.txt", doc_content, "text/plain")}
    )
    assert upload_res.status_code == 200

    # 2. Supported query
    query_supported = "What voltage does the device operate at?"
    res_supported = client.post(
        "/api/v1/chat",
        json={"user_id": 100, "query": query_supported}
    )
    assert res_supported.status_code == 200
    data_supported = res_supported.json()
    
    assert data_supported["status"] == "SUPPORTED"
    assert "230 V" in data_supported["answer"] or "230" in data_supported["answer"]
    assert len(data_supported["sources"]) > 0
    assert any("device_specs.txt" in s["filename"] for s in data_supported["sources"])

    # 3. Uncertain query
    query_uncertain = "What is the manufacturing cost?"
    res_uncertain = client.post(
        "/api/v1/chat",
        json={"user_id": 100, "query": query_uncertain}
    )
    assert res_uncertain.status_code == 200
    data_uncertain = res_uncertain.json()

    assert data_uncertain["status"] == "UNCERTAIN"
    assert data_uncertain["uncertainty_reason"] is not None

def test_a_supported_aurora_x1():
    # Test A — SUPPORTED single document
    doc_content = b"The Aurora X1 operates at 12 V DC. It has a lightweight aluminum body."
    client.post(
        "/api/v1/documents",
        data={"user_id": 200},
        files={"file": ("Doc_A_Aurora.txt", doc_content, "text/plain")}
    )

    res = client.post(
        "/api/v1/chat",
        json={"user_id": 200, "query": "What is the operating voltage of the Aurora X1?"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUPPORTED"
    assert "12 V DC" in data["answer"] or "12 V" in data["answer"]
    assert len(data["sources"]) > 0
    assert any("Doc_A_Aurora.txt" in s["filename"] for s in data["sources"])

def test_b_uncertain_aurora_x1():
    # Test B — UNCERTAIN missing retail price
    res = client.post(
        "/api/v1/chat",
        json={"user_id": 200, "query": "What is the retail price of the Aurora X1?"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "UNCERTAIN"
    assert data["uncertainty_reason"] is not None
    assert "$" not in data["answer"] and "500" not in data["answer"]

def test_c_conflicting_multi_document():
    # Test C — CONFLICTING 12V vs 24V across two documents
    user_id = 300
    doc_a = b"The Aurora X1 operates at 12 V DC. Specifications document A."
    doc_b = b"The Aurora X1 operates at 24 V DC. Specifications document B."

    up_a = client.post(
        "/api/v1/documents",
        data={"user_id": user_id},
        files={"file": ("RAG_Backend_Test_Document.txt", doc_a, "text/plain")}
    )
    assert up_a.status_code == 200

    up_b = client.post(
        "/api/v1/documents",
        data={"user_id": user_id},
        files={"file": ("RAG_Conflict_Test_Document.txt", doc_b, "text/plain")}
    )
    assert up_b.status_code == 200

    res = client.post(
        "/api/v1/chat",
        json={"user_id": user_id, "query": "What is the operating voltage of the Aurora X1?"}
    )
    assert res.status_code == 200
    data = res.json()

    assert data["status"] == "CONFLICTING"
    assert "12 V DC" in data["answer"] or "12 V" in data["answer"]
    assert "24 V DC" in data["answer"] or "24 V" in data["answer"]
    
    # Sources from both documents must be present
    filenames = [s["filename"] for s in data["sources"]]
    assert any("RAG_Backend_Test_Document.txt" in fn for fn in filenames)
    assert any("RAG_Conflict_Test_Document.txt" in fn for fn in filenames)

    # Check contradiction_source_ids on claims
    assert len(data["claims"]) > 0
    assert len(data["claims"][0]["contradiction_source_ids"]) > 0

def test_d_unrelated_document_no_conflict():
    # Test D — Unrelated document for Device Y (48 V DC) does not conflict with Aurora X1 (12 V DC)
    user_id = 400
    doc_aurora = b"The Aurora X1 operates at 12 V DC."
    doc_device_y = b"Device Y operates at 48 V DC."

    client.post(
        "/api/v1/documents",
        data={"user_id": user_id},
        files={"file": ("Aurora_Specs.txt", doc_aurora, "text/plain")}
    )
    client.post(
        "/api/v1/documents",
        data={"user_id": user_id},
        files={"file": ("DeviceY_Specs.txt", doc_device_y, "text/plain")}
    )

    res = client.post(
        "/api/v1/chat",
        json={"user_id": user_id, "query": "What is the operating voltage of the Aurora X1?"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUPPORTED"
    assert "12 V DC" in data["answer"] or "12 V" in data["answer"]

def test_e_concise_answer():
    # Test E — Concise answer check (no raw context dump)
    user_id = 500
    long_doc = b"The Aurora X1 operates at 12 V DC. This document contains 50 lines of background details, history, company profile, manufacturing facilities, engineering teams, and administrative notes that should not be dumped raw into answers."
    
    client.post(
        "/api/v1/documents",
        data={"user_id": user_id},
        files={"file": ("Long_Doc.txt", long_doc, "text/plain")}
    )

    res = client.post(
        "/api/v1/chat",
        json={"user_id": user_id, "query": "What is the operating voltage of the Aurora X1?"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUPPORTED"
    # Ensure answer is concise (< 200 chars) and does not dump raw background text
    assert len(data["answer"]) < 200
    assert "administrative notes" not in data["answer"]

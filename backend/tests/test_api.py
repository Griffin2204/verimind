import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "services" in data
    assert data["services"]["database"] == "healthy"

def test_chat_validation_error():
    response = client.post("/api/v1/chat", json={"user_id": 1, "query": ""})
    assert response.status_code == 400
    data = response.json()
    assert "error" in data

def test_document_upload_and_chat_flow():
    # Upload TXT file
    file_content = b"The device operates at 230 V AC and 50 Hz. Maximum weight is 5 kg."
    upload_res = client.post(
        "/api/v1/documents",
        data={"user_id": 1},
        files={"file": ("specs.txt", file_content, "text/plain")}
    )
    assert upload_res.status_code == 200
    upload_data = upload_res.json()
    assert upload_data["status"] == "processed"
    assert upload_data["chunk_count"] > 0
    doc_id = upload_data["document_id"]

    # Chat query about document
    chat_res = client.post(
        "/api/v1/chat",
        json={"user_id": 1, "query": "What voltage does the device operate at?"}
    )
    assert chat_res.status_code == 200
    chat_data = chat_res.json()
    assert chat_data["status"] in ["SUPPORTED", "UNCERTAIN"]
    assert len(chat_data["sources"]) > 0

    # Retrieve source details
    source_id = chat_data["sources"][0]["source_id"]
    source_res = client.get(f"/api/v1/sources/{source_id}")
    assert source_res.status_code == 200
    source_data = source_res.json()
    assert source_data["document_id"] == doc_id

def test_memory_crud_and_confirm():
    # Add memory
    mem_res = client.post(
        "/api/v1/memory",
        json={"user_id": 1, "text": "I prefer Python programming language.", "type": "preference"}
    )
    assert mem_res.status_code == 200
    mem_data = mem_res.json()
    mem_id = mem_data["id"]

    # Get memories
    get_res = client.get("/api/v1/memory?user_id=1")
    assert get_res.status_code == 200
    assert any(m["id"] == mem_id for m in get_res.json())

    # Confirm memory
    confirm_res = client.post("/api/v1/memory/confirm", json={"memory_id": mem_id})
    assert confirm_res.status_code == 200
    assert confirm_res.json()["validation_status"] == "validated"

    # Delete memory
    del_res = client.delete(f"/api/v1/memory/{mem_id}")
    assert del_res.status_code == 200

def test_feedback_submission():
    fb_res = client.post(
        "/api/v1/feedback",
        json={
            "user_id": 1,
            "answer_id": "ans_101",
            "query": "What is the voltage?",
            "answer": "230 V AC",
            "label": "correct"
        }
    )
    assert fb_res.status_code == 200
    assert fb_res.json()["status"] == "received"

# REST API Contract

Base path: /api/v1

## GET /health
Return service status for database, vector store and Ollama.

## POST /api/v1/chat
Request:
{
  "user_id": 1,
  "query": "What does my document say about testing?",
  "conversation_id": null
}

Response:
{
  "answer": "...",
  "status": "SUPPORTED",
  "sources": [
    {
      "source_id": "src_123",
      "document_id": 12,
      "filename": "example.pdf",
      "page": 4,
      "chunk_id": "chunk_17",
      "snippet": "..."
    }
  ],
  "claims": [
    {
      "text": "...",
      "status": "SUPPORTED",
      "confidence": 0.92,
      "source_ids": ["src_123"]
    }
  ],
  "uncertainty_reason": null
}

## POST /api/v1/documents
Multipart upload. Accept PDF, DOCX and TXT. Return document ID, processing status and chunk count.

## GET /api/v1/memory?user_id=1
Return memory records.

## POST /api/v1/memory/confirm
Request: {"memory_id": 42}

## DELETE /api/v1/memory/{memory_id}
Delete or soft-delete according to implementation.

## POST /api/v1/feedback
Request:
{"user_id":1,"answer_id":"ans_123","label":"correct","correction":null}

Labels: correct, incorrect, not_enough_evidence, correction.

## GET /api/v1/sources/{source_id}
Return filename, page, section, chunk and snippet.

## POST /api/v1/conflicts/{conflict_id}/resolve
Request: {"resolution":"keep_new"}
Allowed: keep_old, keep_new, keep_both.

## Errors
Use:
{"error":{"code":"DOCUMENT_NOT_FOUND","message":"Document was not found."}}

Never return raw stack traces.

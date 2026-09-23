# Backend API Integration

The EXISTING FastAPI backend is authoritative.

First inspect:
`http://localhost:8000/docs`

Also inspect the backend route definitions before writing API calls.

Do not invent endpoint names, HTTP methods, request bodies, or response fields when they already exist.

## Observed chat response shape

The backend currently returns data similar to:

```json
{
  "answer": "The provided documents give conflicting operating voltages...",
  "status": "CONFLICTING",
  "sources": [
    {
      "source_id": "src_10_doc_10_chunk_0",
      "document_id": 10,
      "filename": "RAG_Conflict_Test_Document.pdf",
      "page": 1,
      "chunk_id": "doc_10_chunk_0",
      "snippet": "..."
    }
  ],
  "claims": [
    {
      "text": "...",
      "status": "CONFLICTING",
      "confidence": 0.5,
      "source_ids": [],
      "contradiction_source_ids": []
    }
  ],
  "uncertainty_reason": "..."
}
```

Use the live Swagger/backend implementation if the exact schema differs.

## Status rendering

### SUPPORTED
Show the answer prominently, clear supported status, and relevant evidence.

### UNCERTAIN
Show the answer, clear uncertainty status, `uncertainty_reason` when available, and sources if returned. Do not make uncertain information look confirmed.

### CONFLICTING
Show obvious conflict status, the answer explaining the disagreement, both relevant sources, and claims/contradiction details where useful. Never silently choose one conflicting value.

## Sources

For each source show:
- filename
- page
- short snippet

Put technical IDs such as source ID/chunk ID/document ID inside expandable details.

## Upload

Use the actual upload endpoint from Swagger.

Show:
- selected file
- uploading state
- success
- failure

Support the file types accepted by the backend.

## Health

If `/health` is available, use it for a lightweight connection indicator. Do not poll it aggressively.

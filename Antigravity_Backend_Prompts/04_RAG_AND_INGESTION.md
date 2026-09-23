# RAG and Ingestion

Pipeline:
Upload → validate → hash → extract → normalize → chunk → embed → Chroma + SQLite.

## Parsers
PDF: PyMuPDF
DOCX: python-docx
TXT: UTF-8

Preserve filename, document_id, page and section where possible.

## Chunking
Start around 500–800 tokens with 50–100 token overlap. Make configurable. Avoid splitting useful headings when practical.

## Embeddings
Use a configurable local sentence-transformers model.

## Chroma metadata
Store document_id, chunk_id, filename, page, section and created_at.

## Retrieval
Embed query → top-k search → relevance threshold → optional adjacent-chunk deduplication → return provenance.

If nothing passes the threshold, return no evidence rather than inventing evidence.

## Grounded prompt
Tell the model to:
- use supplied evidence for document facts
- distinguish evidence from inference
- never fabricate citations
- say when evidence is insufficient
- stay concise

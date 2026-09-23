# Database Design

Use SQLAlchemy + SQLite.

## users
id, name, created_at

## memories
id, user_id, text, type, source, confidence, validation_status, created_at, updated_at

validation_status:
pending, validated, superseded, rejected

## documents
id, user_id, filename, file_hash, uploaded_at

## chunks
id, document_id, page, section, text, embedding_id, created_at

Vectors live in Chroma; relational metadata stays in SQLite.

## feedback
id, user_id, answer_id, query, answer, label, correction, created_at

## conflicts
id, old_memory_id, new_memory_id, status, resolution, created_at, resolved_at

## audit_events
id, user_id, event, timestamp, metadata

Enable foreign keys, use UTC timestamps, index user_id/validation_status/document_id and never store secrets.

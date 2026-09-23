# Test Plan

Use pytest.

## Unit
- PDF/DOCX/TXT parsing
- unsupported file rejection
- oversized/corrupt upload handling
- chunking
- metadata preservation
- retrieval relevance
- empty retrieval
- memory CRUD
- conflict detection/resolution
- supported/uncertain/conflicting verification

## API
Test health, chat validation, upload, memory, feedback, sources and conflicts.

## Integration
Seed:
"The device operates at 230 V AC and 50 Hz."

Question:
"What voltage does the device operate at?"

Expected:
230 V AC, SUPPORTED, source returned.

Question:
"What is the manufacturing cost?"

Expected:
UNCERTAIN and no fabricated value.

Run the complete test suite before completion.

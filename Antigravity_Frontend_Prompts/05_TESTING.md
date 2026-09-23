# Frontend Testing & Verification

## Test 1 — SUPPORTED
Question:
`What is the operating voltage of the Aurora X1?`

Expected:
- answer displayed
- SUPPORTED status
- relevant source displayed

## Test 2 — UNCERTAIN
Question:
`What is the retail price of the Aurora X1?`

Expected:
- UNCERTAIN status
- no invented price
- uncertainty explanation when returned

## Test 3 — CONFLICTING
With both conflict PDFs uploaded:
`What is the operating voltage of the Aurora X1?`

Expected:
- CONFLICTING status
- disagreement explained
- 12 V evidence visible
- 24 V evidence visible
- both source documents visible

## Test 4 — Upload
Upload a supported PDF. Verify the actual backend request and success/failure feedback.

## Test 5 — Backend offline
Stop FastAPI. Verify the frontend does not crash and shows a friendly connection error.

## Test 6 — Empty query
Do not send an invalid empty request.

## Test 7 — Long content
Verify no overflow or broken layout.

## Quality
Run:
- `npm run build`
- `npm run lint` if configured

Fix build errors.

Confirm:
- real API integration
- no fake data
- no normal-use console errors
- responsive layout
- source provenance preserved

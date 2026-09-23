# Implementation Instructions

## 1. Inspect
Before coding:
1. Inspect the existing frontend directory.
2. Inspect `http://localhost:8000/docs`.
3. Inspect backend routes/schemas.
4. Determine exact request/response formats.
5. Check whether React/Vite already exists.

Do not overwrite an existing working frontend without inspection.

## 2. Setup
If no frontend exists, create a Vite React JavaScript project.

## 3. API client
Centralize the backend base URL:

```js
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
```

Do not scatter backend URLs through components.

## 4. Chat
Implement:
- send question
- Enter to send
- Shift+Enter for newline if using textarea
- loading state
- disabled send while loading
- user message
- assistant response
- response metadata

## 5. Evidence
Render all returned source information. Do not discard source ID, document ID, filename, page, chunk ID, or snippet.

## 6. Status
Use the backend `status` field. Do not infer status from answer text.

## 7. Upload
Use the real backend document-upload endpoint. Do not fake success.

## 8. Errors
Friendly messages only.

Backend offline:
`Cannot connect to the backend. Make sure the FastAPI server is running on port 8000.`

Generic:
`Something went wrong while processing your request.`

Do not expose stack traces to normal users.

## 9. Polish
Implement loading indicator, empty state, auto-scroll to latest message, disabled states, source cards, and responsive CSS.

Avoid excessive animations.

## 10. Verification
Test the actual backend with supported, uncertain, and conflicting questions; source rendering; upload; backend offline; and mobile viewport.

Do not hardcode Aurora X1 responses.

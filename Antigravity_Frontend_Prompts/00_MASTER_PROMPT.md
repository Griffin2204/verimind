# MASTER PROMPT — React Frontend for Evidence-Grounded RAG Chatbot

Build the complete frontend for the existing Hackathon Chatbot backend.

IMPORTANT:
- The backend already exists and has been tested.
- DO NOT rebuild the backend.
- Read ALL `.md` files in this folder before implementing.
- Treat these files as the authoritative frontend implementation specification.
- Inspect the existing backend through FastAPI Swagger at `http://localhost:8000/docs`.
- Use the actual backend routes and schemas; do not invent API contracts.

## Stack
- React
- Vite
- JavaScript
- CSS
- Fetch or Axios
- Keep dependencies minimal.

## Required Features
1. Chat with the real backend.
2. Display concise assistant answers.
3. Display `SUPPORTED`, `UNCERTAIN`, and `CONFLICTING` status.
4. Display evidence/source provenance.
5. Upload documents through the real backend endpoint.
6. Handle loading, errors, empty states, and backend-offline state.
7. Support feedback/memory UI if the existing backend exposes usable endpoints.
8. Responsive desktop/mobile UI.

## Backend
Default API base URL:
`http://localhost:8000`

Make configurable through:
`VITE_API_BASE_URL`

## Definition of Done
The frontend must:
- start with Vite
- connect to the real backend
- send real chat requests
- render real responses
- preserve source metadata
- distinguish all three policy states
- upload real documents
- handle failures gracefully
- build successfully
- contain no fake/demo API responses
- include run instructions in README

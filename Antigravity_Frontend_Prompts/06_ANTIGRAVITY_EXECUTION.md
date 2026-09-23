# Antigravity Execution Order

Read ALL `.md` files in this folder before implementing.

Execute:
1. Inspect existing frontend.
2. Inspect backend Swagger at `http://localhost:8000/docs`.
3. Inspect actual backend routes and schemas.
4. Determine exact API contracts.
5. Create or repair React/Vite frontend.
6. Implement centralized API service.
7. Implement chat.
8. Implement SUPPORTED / UNCERTAIN / CONFLICTING rendering.
9. Implement source/evidence cards.
10. Implement document upload.
11. Implement health/connection indication if appropriate.
12. Implement loading/error/empty states.
13. Implement responsive styling.
14. Run build/lint/tests.
15. Start frontend and manually verify against the live backend.

## Critical rules

- Follow every `.md` file in this folder.
- Existing backend is authoritative for API contracts.
- Do not rebuild or unnecessarily modify the backend.
- Do not use mock/fake data in the final frontend.
- Do not hardcode Aurora X1 responses.
- Preserve all useful source provenance.
- Never hide conflicts.
- Never make UNCERTAIN look like confirmed information.
- Do not claim something works without testing it.

## Backend command

```powershell
cd "C:\Users\aryan.pawar\OneDrive\Desktop\SPIT\SEM 3\TCET HACK\backend"
..\venv\Scripts\python.exe -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

## Frontend

Use the actual package scripts, normally:

```bash
npm install
npm run dev
```

## Final report

Report:
- files created/changed
- dependencies
- endpoints integrated
- features completed
- build/lint/test results
- manual test results
- frontend URL
- remaining issues

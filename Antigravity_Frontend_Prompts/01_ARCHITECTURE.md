# Frontend Architecture

Suggested structure:

```text
frontend/
├── src/
│   ├── components/
│   │   ├── Chat/
│   │   ├── Sources/
│   │   ├── Upload/
│   │   ├── Memory/
│   │   └── common/
│   ├── pages/
│   ├── services/
│   ├── hooks/
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── .env.example
├── package.json
└── README.md
```

Adapt this to the existing project if a frontend already exists.

Keep API calls in service modules rather than scattering fetch logic across components.

Maintain state for:
- messages
- current input
- loading
- error
- upload state
- selected/expanded source
- backend availability

Handle network failures, HTTP 400/404/500, malformed responses, upload failures, and backend offline.

Never crash the entire UI because one request fails.

# Evidence-Grounded RAG Chatbot — React/Vite Frontend

Clean, modern React frontend interface for the Evidence-Grounded RAG Chatbot backend.

## Features
- **Real Backend Integration**: Connects directly to FastAPI backend endpoints (`/health`, `/api/v1/chat`, `/api/v1/documents`, `/api/v1/memory`, `/api/v1/feedback`).
- **Policy Status Badges**: Clear visual badges & distinct styling for `SUPPORTED`, `UNCERTAIN`, and `CONFLICTING` claims.
- **Source Provenance Cards**: Renders document file names, page numbers, text snippets, and expandable technical details (source ID, document ID, chunk ID).
- **Cross-Document Disagreement Visualizer**: Highlights multi-document conflicting evidence explicitly without taking sides.
- **Document Management**: Drag-and-drop file upload supporting PDF, DOCX, and TXT files.
- **Persistent User Memory**: Panel to view, add, confirm, or delete personalized user facts & preferences.
- **Backend Health Monitor**: Real-time status indicator tracking server availability.
- **Responsive Layout**: Designed for both desktop and mobile viewports.

## Prerequisites
- Node.js (v18+)
- Running FastAPI Backend at `http://localhost:8000`

## Installation & Setup

1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   cmd /c npm install
   ```

3. Configure Environment:
   Copy `.env.example` to `.env`:
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   ```

4. Start Development Server:
   ```bash
   cmd /c npm run dev
   ```

5. Build for Production:
   ```bash
   cmd /c npm run build
   ```

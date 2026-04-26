# Athena AI

Athena AI is a full-stack application for:
- unbiased conversational reasoning,
- document bias analysis,
- document follow-up chat grounded in uploaded content.

It uses a React frontend, a FastAPI backend, Firebase Authentication/Firestore, and Google Gemini.

## Project Structure

```text
Athena-AI/
├── api/                      # FastAPI backend + serverless handlers
│   ├── main.py               # Primary API app (chat, upload, documents)
│   ├── _gemini.py            # Gemini prompting/response helpers
│   ├── _firebase.py          # Firebase Admin initialization
│   ├── _auth.py              # Firebase token verification
│   └── requirements.txt
├── frontend/                 # React + CRACO + Tailwind UI
│   ├── src/components/       # Chat UI, upload UI, layout components
│   ├── src/pages/            # Auth and dashboard pages
│   └── package.json
└── vercel.json               # Deployment config
```

## Features

### 1) Athena Chat
- Authenticated chat endpoint (`/api/chat`) for unbiased reasoning.
- Conversation history stored in Firestore.
- Bias-awareness tagging for specific demographic-selection prompts.

### 2) Document Bias Analysis
- Upload files to `/api/upload`.
- Extracts text and analyzes with Gemini for potential demographic bias.
- Stores analysis metadata in Firestore.

### 3) Document Follow-up Chat
- After analysis, frontend can ask Athena follow-up questions specific to that file (`/api/upload/chat`).
- Chat prompt includes:
  - filename,
  - extracted document text (bounded),
  - initial analysis,
  - recent doc-chat turns.

### 4) Spreadsheet Support
- `.csv` / `.tsv` extraction via Python CSV parser.
- `.xlsx` extraction via lightweight ZIP/XML parsing.
- Readability checks block clearly garbled/non-text uploads.

---

## Tech Stack

### Frontend
- React 19
- React Router
- Axios
- Tailwind + Radix UI components
- Firebase Web SDK

### Backend
- FastAPI
- Firebase Admin SDK (Auth + Firestore)
- Google GenAI SDK (`google-genai`)

---

## Environment Variables

Create env files/secrets for both backend and frontend.

### Backend (`api`)
Required:

- `GEMINI_API_KEY`
- `FIREBASE_PROJECT_ID`
- `FIREBASE_PRIVATE_KEY_ID`
- `FIREBASE_PRIVATE_KEY`
- `FIREBASE_CLIENT_EMAIL`
- `FIREBASE_CLIENT_ID`

Optional/defaulted:
- `FIREBASE_TYPE` (default: `service_account`)
- `FIREBASE_AUTH_URI`
- `FIREBASE_TOKEN_URI`
- `FIREBASE_AUTH_PROVIDER_CERT_URL`
- `FIREBASE_CLIENT_CERT_URL`
- `FIREBASE_STORAGE_BUCKET`

> Note: `FIREBASE_PRIVATE_KEY` should preserve newlines (often provided with `\n` in hosted envs).

### Frontend (`frontend`)
- `REACT_APP_BACKEND_URL` (example: `http://localhost:8000`)
- `REACT_APP_FIREBASE_API_KEY`
- `REACT_APP_FIREBASE_AUTH_DOMAIN`
- `REACT_APP_FIREBASE_PROJECT_ID`
- `REACT_APP_FIREBASE_STORAGE_BUCKET`
- `REACT_APP_FIREBASE_MESSAGING_SENDER_ID`
- `REACT_APP_FIREBASE_APP_ID`
- `REACT_APP_FIREBASE_MEASUREMENT_ID` (optional)

---

## Local Development

## 1) Backend

```bash
cd api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend health check:

```bash
curl http://localhost:8000/api/health
```

## 2) Frontend

```bash
cd frontend
npm install
npm start
```

App runs on `http://localhost:3000` by default.

---

## API Overview

### `POST /api/chat`
Send a user prompt and receive Athena response.

Request body:
```json
{
  "message": "How can I evaluate candidates fairly?",
  "conversation_id": "optional-id"
}
```

### `GET /api/conversations`
List the authenticated user's conversations.

### `GET /api/conversations/{conversation_id}/messages`
List messages in a conversation.

### `POST /api/upload`
Upload a document/spreadsheet for bias analysis.

Response includes:
- `analysis`
- `document_text` (truncated context for follow-up chat)

### `POST /api/upload/chat`
Ask follow-up questions about an analyzed document.

Request body:
```json
{
  "filename": "policy.xlsx",
  "document_text": "...",
  "analysis": "...",
  "message": "Rewrite this in neutral language",
  "history": [{ "role": "user", "content": "..." }]
}
```

### `GET /api/documents`
List saved document analyses for the authenticated user.

---

## Build & Checks

### Frontend production build
```bash
cd frontend
npm run build
```

### Basic backend syntax check
```bash
python -m py_compile api/main.py api/_gemini.py
```

---

## Deployment Notes

- This repo includes `vercel.json` and serverless-style `api/*.py` handlers.
- Ensure all backend secrets are configured in deployment environment.
- Set `REACT_APP_BACKEND_URL` to your deployed backend base URL.

---

## Known Constraints

- XLSX extraction is intentionally lightweight; heavily formatted/complex formulas may not fully render as natural text.
- Readability heuristic can reject very short uploads.
- Document chat context is bounded (truncated text + short history) to manage token/payload size.


No license file is currently defined in this repository.# Here are your Instructions

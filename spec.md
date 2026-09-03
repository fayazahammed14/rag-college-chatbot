# Spec Driven Development
## Building a RAG-Based College Chatbot — CampusMind AI

---

## Project Overview & Tech Stack

### Project Overview
Build a full-stack AI-powered college information assistant called **CampusMind AI** that answers student questions using Retrieval-Augmented Generation (RAG). The platform must let admins upload, update, and delete official college documents (PDFs, notices, FAQs covering admissions, departments, courses, fees, exams, academic calendar, hostel, library, clubs, placements, scholarships, policies, events), process and index that content, retrieve the most relevant passages for any student question, and generate an answer using an LLM that is grounded strictly in the retrieved content. Every answer must show the source document it came from. When no relevant content exists, the system must clearly say so instead of guessing.

### Tech Stack
**Frontend:** React (Vite), Tailwind CSS, `@supabase/supabase-js` (auth), Axios (calls to backend), React Router, Zustand (chat/session state), lucide-react icons.

**Backend:** Python, FastAPI, Pydantic, `supabase-py` (Supabase client + JWT verification), python-multipart (file uploads), pypdf (text extraction).

**AI Integration:** Google Generative AI SDK (Gemini) — `text-embedding-004` for embeddings, `gemini-2.0-flash` (or latest available Gemini flash model) for answer generation. LangChain's `RecursiveCharacterTextSplitter` is available for chunking.

**Database, Auth & Vector Store:** Supabase — Postgres for all data, `pgvector` extension for embeddings, and Supabase Auth for signup/login/session handling. One project, one dashboard, one set of credentials.

**Deployment:** GitHub → Vercel (frontend) → Render (backend) → Supabase (auth + database + vector search).

---

## Authentication

Authentication is handled by **Supabase Auth**. The frontend uses `@supabase/supabase-js` directly for signup, login, logout, and session persistence (no custom password/JWT code to write or maintain). On signup, a matching row is created in a `profiles` table (`id` = the Supabase auth user id, `name`, `role: student | admin`, `created_at`) since role separation isn't part of the default auth session. Every protected backend request must include the Supabase access token in the `Authorization` header; the backend verifies it via `supabase-py` and reads the caller's role from `profiles` before allowing admin-only actions. Supabase Row Level Security policies on every table double-check the same rule at the database layer, so authorization isn't enforced by the backend alone.

---

## Document Pipeline & RAG Core

### Document Management (Admin Only)
Admins must be able to upload PDF documents, update a document's title/metadata or replace its file (triggering reprocessing), delete a document (cascading delete of its chunks and embeddings), and view all documents with processing status (`processing | ready | failed`) and metadata (title, page count, upload date, uploader).

### Document Processing Pipeline
On upload or replace, the backend must: extract text from the PDF, split it into overlapping chunks (target ~500-800 tokens per chunk with ~100 token overlap), generate an embedding for each chunk via Gemini's embedding model, and insert each chunk with its embedding, source document reference, and page number into the `document_chunks` table.

### Retrieval-Augmented Generation Pipeline
When a student submits a question: embed the question using the same embedding model, call the `match_chunks` Postgres function via Supabase RPC to retrieve the top-k most relevant chunks by cosine similarity (k configurable, default 5), construct a prompt that instructs the LLM to answer **only** using the retrieved chunks, call Gemini to generate the answer, and return the answer along with the list of source documents/pages used. If similarity scores for all retrieved chunks fall below a relevance threshold, the system must return a clear "I don't have information on that in the uploaded documents" response instead of calling the LLM with irrelevant context.

### Conversation Context
Each chat must belong to a Conversation. Follow-up questions must be answerable using recent conversation history as additional context alongside the retrieved chunks, so the assistant can resolve references like "what about the second one?"

---

## Frontend Pages

The application uses React Router.

- `/login` - Supabase-backed email/password login, session persisted via Zustand + Supabase client.
- `/register` - Signup form (creates the auth user and the matching `profiles` row with role `student`).
- `/chat` - Main chat interface: message list, input box, typing/loading indicator, source citation chips shown under each AI answer, and a sidebar listing past conversations.
- `/chat/:conversationId` - Resume an existing conversation with full history loaded.
- `/admin/documents` - Admin-only page: upload form, table of documents with status badges, edit/replace and delete actions, processing progress indicator.
- `/settings` - Basic profile view and logout.

---

## Backend Architecture & Database Tables

### Backend Architecture
- **Routers:** `profile_router.py`, `document_router.py`, `chat_router.py` - handle HTTP routing and request validation via Pydantic models only.
- **Services:** `auth_service.py` (verifies Supabase tokens, resolves role), `document_service.py` (extraction + chunking orchestration), `embedding_service.py` (calls to Gemini embeddings), `retrieval_service.py` (Supabase RPC vector search), `rag_service.py` (prompt construction + generation + source attribution), `chat_service.py` (conversation/message persistence).
- **Models:** Pydantic schemas matching each Supabase table below.
- **Config:** `settings.py` (env vars), `db.py` (Supabase client initialization).

### Database Tables (Supabase / Postgres)
- **profiles:** `id` (= auth.users.id), `name`, `role: student | admin`, `created_at`.
- **documents:** `id`, `title`, `filename`, `uploaded_by`, `status: processing | ready | failed`, `page_count`, `uploaded_at`, `updated_at`.
- **document_chunks:** `id`, `document_id` (FK, cascade delete), `chunk_index`, `text`, `embedding` (vector column, indexed with pgvector), `page_number`.
- **conversations:** `id`, `user_id`, `title`, `created_at`, `updated_at`.
- **messages:** `id`, `conversation_id` (FK), `role: user | assistant`, `content`, `sources` (jsonb array of `{document_id, document_title, page_number}`), `created_at`.

---

## API Endpoints

**Health & Profile**
- `GET /api/health` - System heartbeat.
- `GET /api/profile/me` - Verify the Supabase token and return the caller's profile + role.

**Documents (admin only)**
- `POST /api/documents/upload` - Upload a PDF and start processing.
- `GET /api/documents` - List all documents with status.
- `GET /api/documents/:id/status` - Poll processing status.
- `PUT /api/documents/:id` - Update title/metadata or replace the file (re-triggers processing).
- `DELETE /api/documents/:id` - Delete a document and its chunks.

**Chat**
- `POST /api/chat/ask` - Body: `{ conversationId?, question }`. Runs the RAG pipeline, returns `{ answer, sources, conversationId }`.
- `GET /api/conversations` - List the current user's conversations.
- `GET /api/conversations/:id` - Fetch a conversation with full message history.
- `DELETE /api/conversations/:id` - Delete a conversation.

---

## Folder Structure & Development Phases

### Backend Structure
```
server/
└── app/
    ├── main.py
    ├── config/
    │   ├── settings.py
    │   └── db.py
    ├── routers/
    │   ├── profile_router.py
    │   ├── document_router.py
    │   └── chat_router.py
    ├── services/
    │   ├── auth_service.py
    │   ├── document_service.py
    │   ├── embedding_service.py
    │   ├── retrieval_service.py
    │   ├── rag_service.py
    │   └── chat_service.py
    ├── models/
    │   ├── profile.py
    │   ├── document.py
    │   ├── chunk.py
    │   ├── conversation.py
    │   └── message.py
    └── utils/
        └── security.py
requirements.txt
.env
```

### Frontend Structure
```
client/
└── src/
    ├── components/
    │   ├── ChatWindow/
    │   ├── MessageBubble/
    │   ├── SourceChip/
    │   ├── Sidebar/
    │   └── ProtectedRoute/
    ├── pages/
    │   ├── Login.jsx
    │   ├── Register.jsx
    │   ├── Chat.jsx
    │   ├── AdminDocuments.jsx
    │   └── Settings.jsx
    ├── store/
    │   └── authStore.js
    └── services/
        ├── supabaseClient.js
        └── api.js
```

### Development Phases
- **Phase 1:** Project setup - Supabase project created, `pgvector` extension enabled, FastAPI + Supabase client connected, React app scaffold with Supabase Auth wired up (signup/login/logout), protected routes on both ends, `profiles` table + RLS policies.
- **Phase 2:** Admin document upload + update + delete, text extraction + chunking pipeline, stored in `documents`/`document_chunks` tables (verify chunks exist in Supabase before adding embeddings).
- **Phase 3:** Add the `embedding` column and `match_chunks` SQL function, generate embeddings for each chunk via Gemini; verify a test query returns relevant chunks by similarity.
- **Phase 4:** Full RAG pipeline - retrieval + grounded prompt + Gemini generation + source attribution + "not found" fallback.
- **Phase 5:** Chat UI - conversation list, message history, source chips, loading states, admin document table with status badges and edit/replace flow.
- **Phase 6:** Deployment (Vercel + Render + Supabase) and bonus features if time remains (feedback thumbs, streaming responses, OCR for scanned PDFs, suggested questions).

---

## UI, Security, and Outcome

### UI/UX Requirements
Clean chat-app aesthetic (ChatGPT-style), fully responsive, message bubbles distinguishing user vs. assistant, typing/loading indicator during generation, source citation chips under each AI answer, admin document table with color-coded status badges, and clear empty/error states.

### Security Requirements
Supabase Auth handles credential storage and session tokens (no custom password code). Row Level Security enabled on every table so a student can only read their own conversations/messages and cannot write to `documents`/`document_chunks`. Admin-only backend routes double-check the caller's role from `profiles` before acting. CORS restricted to the deployed frontend URL. All request bodies validated via Pydantic. `GEMINI_API_KEY` and the Supabase service-role key are never exposed to the frontend — the frontend only ever holds the public anon key. File uploads restricted to PDF type and a max size.

### Final Expected Outcome
A student can log in, ask a college-related question in plain English, and receive an answer generated strictly from officially uploaded documents, with the exact source shown, a graceful fallback when nothing relevant exists, and continuity across follow-up questions - while admins manage the full knowledge base lifecycle (upload, update, delete) from their own panel. The application must be fully deployed and reachable via a public URL.

### AI Coding Agent Implementation Instructions
Build phase by phase - do not request the whole app in one prompt. Keep routers thin; push logic into services. Never call Supabase directly from a router. Never call Gemini directly from a router - always go through `embedding_service` or `rag_service`. Treat every secret as an environment variable. Report the list of files created or changed at the end of every phase before moving to the next.
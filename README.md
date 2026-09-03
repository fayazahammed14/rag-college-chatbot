# CampusMind AI — College Information Assistant (RAG)

CampusMind AI is a full-stack, AI-powered college information assistant built using **Retrieval-Augmented Generation (RAG)**. It allows college administrators to upload official PDF documents (brochures, fee structures, hostel rules, exam schedules, course syllabi, placement records), indexes the content with 768-dimensional vector embeddings using Google Gemini and Supabase `pgvector`, and provides students with an interactive assistant that generates strictly grounded answers with verifiable source document citations.

---

## Architecture Overview

```
                               ┌───────────────────────────┐
                               │     React Client (Vite)   │
                               │  Tailwind CSS + Zustand   │
                               └─────────────┬─────────────┘
                                             │
                       ┌─────────────────────┴─────────────────────┐
                       │                                           │
                       ▼ (Auth / Session)                          ▼ (API Requests + JWT)
        ┌───────────────────────────────┐           ┌───────────────────────────────┐
        │        Supabase Auth          │           │       FastAPI Backend         │
        │  (User Signup/Login/Tokens)   │           │  (Python + Pydantic + Uvicorn)│
        └──────────────┬────────────────┘           └──────────────┬────────────────┘
                       │                                           │
                       │                        ┌──────────────────┴──────────────────┐
                       │                        ▼                                     ▼
                       │           ┌─────────────────────────┐           ┌─────────────────────────┐
                       │           │   Google Gemini API     │           │   Supabase Postgres     │
                       │           │ • text-embedding-004    │           │ • pgvector extension    │
                       │           │ • gemini-2.0-flash      │           │ • match_chunks RPC      │
                       │           └─────────────────────────┘           │ • RLS Security Policies │
                       │                                                 └────────────┬────────────┘
                       └──────────────────────────────────────────────────────────────┘
```

---

## Features

- **Strict RAG Grounding**: The LLM answers solely using retrieved excerpts from official documents.
- **Source Attribution**: Every answer shows clickable citations specifying the document name and page number.
- **Graceful Fallback**: Explicitly states when requested information is not in the uploaded documents rather than hallucinating.
- **Multi-Turn Continuity**: Maintains conversation context to seamlessly resolve follow-up questions.
- **Admin Knowledge Base**: Admins can upload PDFs, replace files, update metadata, monitor vector indexing status (`processing` → `ready` / `failed`), and delete documents.
- **Role-Based Access Control**: Student and Admin roles enforced at both the API layer (FastAPI dependencies) and the database layer (Supabase Row Level Security).
- **ChatGPT-Style UI**: Sleek dark-mode interface with message bubbles, typing indicators, suggested questions, and responsive mobile sidebar.

---

## Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, Vite, Tailwind CSS, `@supabase/supabase-js`, Axios, Zustand, React Router, Lucide React, React Markdown |
| **Backend** | Python 3.10+, FastAPI, Pydantic v2, `supabase-py`, `pypdf`, `langchain-text-splitters`, `google-generativeai` / `google-genai` |
| **Database & Vector** | Supabase (PostgreSQL with `pgvector` extension) |
| **AI Models** | Google Gemini `text-embedding-004` (768-dim embeddings) & `gemini-2.0-flash` (answer generation) |

---

## Prerequisites

Before running the project locally, ensure you have:
1. **Node.js** (v18.0.0 or higher) and `npm`
2. **Python** (v3.10 or higher) and `pip`
3. A free **[Supabase](https://supabase.com/)** account
4. A free **[Google AI Studio (Gemini)](https://aistudio.google.com/)** API key

---

## Step 1: Supabase Setup (Database & Vector Store)

1. Log in to [Supabase](https://supabase.com/) and click **New project**.
2. Go to the **SQL Editor** tab in your Supabase project dashboard.
3. Open [`supabase/schema.sql`](supabase/schema.sql) in this repository, copy its entire contents, paste it into the Supabase SQL Editor, and click **Run**.
   - This enables the `vector` extension.
   - Creates `profiles`, `documents`, `document_chunks`, `conversations`, and `messages` tables.
   - Creates the vector index and the `match_chunks` vector cosine similarity function.
   - Configures Row Level Security (RLS) policies and automatic profile creation triggers.
4. Go to **Project Settings** → **API** and copy:
   - **Project URL** (`https://<project-ref>.supabase.co`)
   - **anon / public key**
   - **service_role key** (keep this secret; only used by the FastAPI backend)

---

## Step 2: Backend Setup (FastAPI)

1. Open a terminal and navigate to the `server/` directory:
   ```bash
   cd server
   ```

2. Create and activate a Python virtual environment:
   - **Windows (PowerShell):**
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - **macOS / Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables in `server/.env`:
   ```env
   SUPABASE_URL=https://your-project-ref.supabase.co
   SUPABASE_KEY=your-supabase-service-role-key
   SUPABASE_ANON_KEY=your-supabase-anon-key
   GEMINI_API_KEY=your-google-gemini-api-key
   ENVIRONMENT=development
   PORT=8000
   FRONTEND_URL=http://localhost:5173
   SIMILARITY_THRESHOLD=0.35
   TOP_K_CHUNKS=5
   ```

5. Start the backend development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   - The API will be available at: `http://localhost:8000`
   - Interactive Swagger API Documentation: `http://localhost:8000/docs`

---

## Step 3: Frontend Setup (React + Vite)

1. Open a second terminal and navigate to the `client/` directory:
   ```bash
   cd client
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Configure environment variables in `client/.env`:
   ```env
   VITE_SUPABASE_URL=https://your-project-ref.supabase.co
   VITE_SUPABASE_ANON_KEY=your-supabase-anon-key
   VITE_BACKEND_URL=http://localhost:8000
   ```

4. Start the Vite development server:
   ```bash
   npm run dev
   ```
   - Open your browser and navigate to: `http://localhost:5173`

---

## Step 4: Initial Admin Setup & Usage Flow

### 1. Create an Account
1. Open `http://localhost:5173/register` and create an account.
2. If you select **Administrator** during registration, the account will be tagged with the `admin` role.
3. Alternatively, you can promote any user to `admin` directly in Supabase SQL Editor:
   ```sql
   UPDATE public.profiles 
   SET role = 'admin' 
   WHERE id = 'USER_UUID_HERE';
   ```

### 2. Upload Official College PDFs (Admin Only)
1. Sign in with your admin account and navigate to **Knowledge Base** (`/admin/documents`).
2. Upload one or more college PDF documents (e.g. *Academic Handbook.pdf*, *Fee Structure.pdf*, *Hostel Guidelines.pdf*).
3. The background pipeline will:
   - Extract page-by-page text using `pypdf`.
   - Chunk text into 500–800 token passages with 100 token overlap using `RecursiveCharacterTextSplitter`.
   - Generate 768-dimensional vector embeddings via Gemini `text-embedding-004`.
   - Store vectors and page metadata in `document_chunks`.
   - Update document status to **Ready** (`ready`).

### 3. Ask Questions (Students & Faculty)
1. Navigate to the **Chat Assistant** (`/chat`).
2. Type a question in natural language (e.g., *"What is the hostel fee and curfew timing?"*).
3. CampusMind AI will:
   - Embed your question.
   - Run vector cosine similarity search via `match_chunks` in Supabase.
   - Synthesize a factual answer using Gemini `gemini-2.0-flash`.
   - Attach interactive source chips showing the cited document and page number.
   - If the topic is not covered in uploaded documents, it will clearly notify you rather than guessing.

---

## API Reference

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/api/health` | System health check | Public |
| `GET` | `/api/profile/me` | Current user profile & role | Authenticated |
| `POST` | `/api/documents/upload` | Upload & index PDF document | Admin only |
| `GET` | `/api/documents` | List all indexed documents | Admin only |
| `GET` | `/api/documents/{id}/status` | Poll document processing status | Admin only |
| `PUT` | `/api/documents/{id}` | Update title or replace PDF file | Admin only |
| `DELETE` | `/api/documents/{id}` | Delete document & cascade embeddings | Admin only |
| `POST` | `/api/chat/ask` | Submit question to RAG pipeline | Authenticated |
| `GET` | `/api/conversations` | List user's conversations | Authenticated |
| `GET` | `/api/conversations/{id}` | Get full chat history | Authenticated |
| `DELETE` | `/api/conversations/{id}` | Delete conversation | Authenticated |

---

## Production Deployment

- **Frontend (Vercel)**:
  - Connect your GitHub repository to Vercel.
  - Set Root Directory to `client`.
  - Add Environment Variables: `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`, `VITE_BACKEND_URL`.
- **Backend (Render / Railway)**:
  - Create a new Web Service pointing to `server/`.
  - Build Command: `pip install -r requirements.txt`.
  - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
  - Add Environment Variables: `SUPABASE_URL`, `SUPABASE_KEY`, `GEMINI_API_KEY`, `FRONTEND_URL`.
- **Database (Supabase)**:
  - Hosted managed PostgreSQL with `pgvector` enabled.

---

## License

This project is licensed under the MIT License.

# CampusMind AI — RAG-Based College Information Assistant

> **CampusMind AI** is an AI-powered college information assistant built using **Retrieval-Augmented Generation (RAG)**. It allows college administrators to upload official PDF documents (brochures, fee structures, hostel rules, exam schedules, course syllabi, placement records), indexes the content with 768-dimensional vector embeddings using Google Gemini and Supabase `pgvector`, and provides students with an interactive assistant that generates strictly grounded answers with verifiable source document citations.

---

## 1. Problem Statement

College students and prospective applicants frequently struggle to find accurate, up-to-date information across dozens of fragmented PDFs, notices, and handbooks (such as admission rules, fee structures, exam guidelines, hostel policies, and placement statistics). Traditional search and generic LLM chatbots either hallucinate or cannot access internal college publications. 

**CampusMind AI** solves this problem by providing a verifiable, multi-turn RAG chatbot that:
- Answers queries **strictly based on official college documents**.
- Provides **verifiable source citations** (document name + page number).
- Gracefully refuses to guess when information is unavailable.
- Offers an **Admin Management Portal** to upload, update, and manage indexed documents seamlessly.

---

## 2. Features

### Core / Must-Have Features
- **Strict RAG Grounding**: The LLM synthesizes answers strictly using retrieved excerpts from verified documents.
- **Source Attribution & Citations**: Every answer displays interactive source chips showing the cited document name and page number.
- **Graceful Fallback**: Explicitly states when requested information is not in the uploaded documents rather than hallucinating.
- **Multi-Turn Chat History**: Maintains conversation context to seamlessly resolve follow-up questions (e.g., *"What about the second one?"*).
- **Admin Knowledge Base Management**:
  - Upload PDF documents.
  - Page-by-page text extraction (`pypdf`) and recursive chunking (`langchain-text-splitters`).
  - 768-dimensional vector embedding generation (`text-embedding-004`).
  - Edit document metadata or replace files (triggers automated re-indexing).
  - Delete documents with cascading chunk & embedding removal.
  - Real-time indexing status tracking (`processing` → `ready` / `failed`).
- **Role-Based Access Control (RBAC)**: Enforces `student` and `admin` roles across both FastAPI API routes and Supabase Row Level Security (RLS) policies.
- **Authentication**: Secure email/password login and registration powered by Supabase Auth with persisted JWT sessions.

### Bonus Features
- **Suggested Questions**: Contextual prompt chips for quick discovery.
- **Answer Feedback**: Built-in thumbs-up / thumbs-down rating for responses.
- **Source Document Highlighting**: Clear breakdown of page numbers and relevance scores.
- **Modern Glassmorphic Dark UI**: Built with React, Tailwind CSS, Lucide icons, and responsive mobile drawer navigation.
- **Conversation Management**: Create new chats, resume past threads, or delete conversation history.

---

## 3. Technology Stack

| Layer | Technologies | Purpose |
|---|---|---|
| **Frontend** | React 18, Vite, Tailwind CSS, Zustand, React Router v6, Lucide React, React Markdown | Interactive, responsive dark-mode SPA client |
| **Backend API** | Python 3.10+, FastAPI, Pydantic v2, Uvicorn | High-performance RESTful API & RAG pipeline |
| **Database & Vector Store** | Supabase (PostgreSQL with `pgvector` extension) | User profiles, documents, metadata & vector cosine similarity search |
| **Embeddings Model** | Google Gemini `text-embedding-004` (768 dimensions) | Document chunk and query vectorization |
| **LLM Reasoning** | Google Gemini `gemini-2.0-flash` | Strict contextual answer synthesis |
| **Document Processing** | `pypdf`, `langchain-text-splitters` | Text extraction and recursive token chunking |
| **Deployment** | Vercel (Frontend), Render (Backend), Supabase (Cloud Database) | Production cloud hosting |

---

## 4. Architecture & RAG Pipeline

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

### RAG Pipeline Flow:
1. **Admin PDF Upload** &rarr; Text extracted page-by-page via `pypdf`.
2. **Chunking** &rarr; `RecursiveCharacterTextSplitter` (500–800 tokens, 100 token overlap).
3. **Embedding** &rarr; Vectors generated via Gemini `text-embedding-004` (768 dimensions).
4. **Storage** &rarr; Stored in Supabase `document_chunks` table with `pgvector` HNSW / IVFFlat index.
5. **Student Query** &rarr; Query is embedded & matched via cosine similarity `match_chunks` function.
6. **LLM Synthesis** &rarr; `gemini-2.0-flash` generates grounded response with exact document title and page number citations.

---

## 5. Live Demo

- **Frontend (Vercel)**: `https://your-project.vercel.app` *(Replace with your deployed Vercel URL)*
- **Demo Admin Account**: `admin@campusmind.edu` / `Admin@12345`

---

## 6. Backend API

- **Backend Base URL (Render)**: `https://rag-college-backend-iq8v.onrender.com`
- **Interactive Swagger Docs**: `https://rag-college-backend-iq8v.onrender.com/docs`
- **Health Check**: `https://rag-college-backend-iq8v.onrender.com/api/health`

---

## 7. Setup Instructions (Run Locally)

### Prerequisites
- **Node.js** (v18.0.0 or higher) and `npm`
- **Python** (v3.10 or higher) and `pip`
- A free **[Supabase](https://supabase.com/)** account
- A free **[Google AI Studio (Gemini)](https://aistudio.google.com/)** API key

---

### Step 1: Database Setup (Supabase)
1. Log in to [Supabase](https://supabase.com/) and create a new project.
2. Open the **SQL Editor** in your Supabase dashboard.
3. Paste the contents of [`supabase/schema.sql`](supabase/schema.sql) and click **Run**.
4. Copy your **Project URL**, **anon key**, and **service_role key** from **Project Settings → API**.

---

### Step 2: Backend Setup (FastAPI)
1. Open a terminal and navigate to `server/`:
   ```bash
   cd server
   ```
2. Create and activate a virtual environment:
   - **Windows**:
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - **macOS / Linux**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create `server/.env` (see Environment Variables section below).
5. Start the backend server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   - API Docs: `http://localhost:8000/docs`

---

### Step 3: Frontend Setup (React + Vite)
1. Open a second terminal and navigate to `client/`:
   ```bash
   cd client
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Create `client/.env` (see Environment Variables section below).
4. Start the frontend development server:
   ```bash
   npm run dev
   ```
   - Local App: `http://localhost:5173`

---

## 8. Environment Variables

### Backend (`server/.env`)
| Variable | Description | Example / Default |
|---|---|---|
| `SUPABASE_URL` | Supabase Project URL | `https://your-project.supabase.co` |
| `SUPABASE_KEY` | Supabase Service Role Secret Key (Keep Private) | `eyJhbGciOi...` |
| `SUPABASE_ANON_KEY` | Supabase Anonymous Public Key | `eyJhbGciOi...` |
| `GEMINI_API_KEY` | Google AI Studio Gemini API Key | `AIzaSy...` |
| `ENVIRONMENT` | Execution environment (`development` / `production`) | `development` |
| `PORT` | Backend server port | `8000` |
| `FRONTEND_URL` | Allowed frontend origin for CORS | `http://localhost:5173` (or Vercel URL) |
| `SIMILARITY_THRESHOLD` | Minimum cosine similarity score for retrieval | `0.35` |
| `TOP_K_CHUNKS` | Number of context chunks retrieved for RAG | `5` |

### Frontend (`client/.env`)
| Variable | Description | Example / Default |
|---|---|---|
| `VITE_SUPABASE_URL` | Supabase Project URL | `https://your-project.supabase.co` |
| `VITE_SUPABASE_ANON_KEY` | Supabase Anonymous Public Key | `eyJhbGciOi...` |
| `VITE_BACKEND_URL` | Backend API URL | `http://localhost:8000` (or Render URL) |

*(Note: Never commit `.env` files or secret keys to GitHub. All sensitive values are ignored via `.gitignore`)*

---

## 9. Deployment Guide (Vercel + Render + Supabase)

### 1. Database (Supabase)
- Database schema and vector tables are deployed via `supabase/schema.sql`.
- Configure Authentication URL Redirects under **Auth &rarr; URL Configuration**:
  - Add your production Vercel frontend URL (`https://your-project.vercel.app/**`).

### 2. Backend (Render)
1. Create a new **Web Service** on Render connected to your GitHub repository.
2. Set **Root Directory**: `server`
3. Set **Runtime**: `Python 3`
4. Set **Build Command**: `pip install -r requirements.txt`
5. Set **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Under **Environment Variables**, add:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `SUPABASE_ANON_KEY`
   - `GEMINI_API_KEY`
   - `FRONTEND_URL` (Set to your Vercel URL, e.g. `https://your-project.vercel.app`)
   - `ENVIRONMENT=production`

### 3. Frontend (Vercel)
1. Import your GitHub repository into Vercel.
2. Set **Root Directory**: `client`
3. Set **Framework Preset**: `Vite`
4. Under **Environment Variables**, add:
   - `VITE_SUPABASE_URL`
   - `VITE_SUPABASE_ANON_KEY`
   - `VITE_BACKEND_URL` (Set to your Render backend URL, e.g. `https://your-backend.onrender.com`)
5. Click **Deploy**.

---

## 10. License

This project is licensed under the MIT License.

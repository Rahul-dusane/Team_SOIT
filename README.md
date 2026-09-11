# HireLens - Multi-Agent Recruitment Intelligence System

HireLens is an AI-powered recruitment platform combining a **React + Vite** frontend with a **FastAPI + LangGraph** backend, providing automated resume ingestion, pgvector similarity search, deterministic candidate-job matching, and LLM-driven recruiter briefings.

---

## 🛠️ Real-World Setup & Execution Guide

### Step 1: Configure Environment Variables (`.env`)
Ensure your `.env` file in the root directory contains your real database connection string and LLM credentials:

```env
# Database Connection (Supabase Cloud PostgreSQL)
DATABASE_URL=postgresql://postgres.grcihwgasjgofsrlhdox:Msc%4014056%24%24@aws-0-ap-south-1.pooler.supabase.com:5432/postgres

# AI LLM Provider Configuration
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash

# Optional API Key Authentication (Leave empty for open local access)
# API_KEY=your_production_secret_key

# Server Port & Frontend API URL
PORT=8000
VITE_API_URL=http://localhost:8000/api/v1
```

---

### Step 2: Start the Real-World FastAPI Backend Server

Open a terminal (PowerShell / Command Prompt) and run:

```powershell
# 1. Set thread safety for multi-threaded reloader
$env:OPENBLAS_NUM_THREADS="1"; $env:OMP_NUM_THREADS="1"

# 2. Start Uvicorn backend server on port 8000
python -m uvicorn main:app --app-dir backend/agentic-ai --reload --port 8000
```

> **Verification**: Open `http://localhost:8000/docs` in your browser to view the interactive FastAPI Swagger documentation, or check health at `http://localhost:8000/api/v1/health`.

---

### Step 3: Start the React Frontend Application

Open a **second terminal** and run:

```powershell
# 1. Install frontend dependencies (if not already installed)
npm install

# 2. Start Vite development server
npm run dev
```

> **Access Application**: Open `http://localhost:5173` in your browser.

---

## 🧪 Production Features Available in Live Mode

1. **Live PDF / DOCX / TXT Resume Upload**:
   - Drag & drop resumes into the UI.
   - Text is parsed, chunked, embedded into 384-dim vectors, and saved directly into PostgreSQL tables (`candidates`, `documents`, `document_chunks`).
2. **Deterministic Matching Engine**:
   - Scores candidates 0–100% across Must-Have Coverage, Preferred Coverage, Experience Fit, Domain Match, and Semantic Similarity.
3. **Live Job Builder**:
   - Define job roles and requirements; saved atomically to PostgreSQL (`jobs`).
4. **Candidate Rankings & Match Breakdowns**:
   - View candidate rankings for any job and inspect visual category breakdowns, matched skills, missing skill gaps, and agent logs.
5. **Robust User & Server Error Handling**:
   - Displays clear error notifications for unsupported file types, oversized files (> 10MB), or server disconnects.

---

## 🧪 Running Automated System Tests

To run the complete 46-test unit and integration test suite:

```powershell
$env:OPENBLAS_NUM_THREADS="1"; $env:OMP_NUM_THREADS="1"; $env:TESTING="true"; python -m pytest backend/agentic-ai/tests -v
```
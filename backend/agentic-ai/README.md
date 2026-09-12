# HireLens — Multi-Agent Recruitment Intelligence System

HireLens is an explainable multi-agent recruitment intelligence platform built with FastAPI, LangGraph, LangChain, spaCy, sentence-transformers, SQLAlchemy, and PostgreSQL/pgvector.

---

## Team Subsystem Architecture

### Member 1 — Agentic AI / LLM / Extraction Engine
- **Resume Agent**: Converts unstructured resumes into strict `CandidateProfile` Pydantic models.
- **Job Agent**: Converts unstructured job descriptions into machine-readable `JobProfile` specifications with requirement weights (1–10).
- **Skill Gap Agent**: Explains missing skills identified by Member 2's matching engine and discovers transferable skills.
- **Evidence Agent**: Audits candidate experience against job requirements and pulls direct verifiable quotes.
- **Recruiter Agent**: Synthesizes the deterministic match score, breakdown, evidence, and gaps into an actionable recruiter briefing.
- **LangGraph Orchestrator**: Manages state transitions, parallel processing, and end-to-end execution.

### Member 2 — Data Science / NLP / Matching Engine
- **5-Tier Skill Matching Hierarchy**: Exact, Equivalent (Alias), Transferable (Matrix), Related (Fuzzy), Missing.
- **100-Point Weighted Scoring Model**: Evaluates Must-Have skills, Preferred skills, Experience duration, Role similarity, Education, Projects, and Domain fit.
- **Evidence Retriever**: Verifies candidate evidence using strict word boundaries (`Java` vs `JavaScript`) and negation/contradiction detection.
- **Skill Gap Engine**: Categorizes gaps into Critical, Moderate, Optional, and Transferable.

### Member 3 — Database, Vector Storage & REST API Services
- **Supabase Cloud PostgreSQL & pgvector**: 384-dimensional vector embeddings (`all-MiniLM-L6-v2`) with isolated vector similarity retrieval (`<->` / `<=>`).
- **Multi-Format Ingestion**: Validated parsing for PDF (with page numbers), DOCX, and TXT.
- **Atomic Match Persistence**: Single-transaction database storage for candidate profiles, jobs, document chunks, match results, requirement assessments, evidence passages, gaps, summaries, and agent logs.
- **REST API Layer**: Production FastAPI service exposing endpoints for upload, candidate/job management, match execution, candidate ranking, and stats dashboard.

---

## Directory Structure

```text
backend/agentic-ai/
├── app/                            # Member 1 Agentic Workflows & Schemas
│   ├── agents/                     # LangChain Resume, Job, Gap, Evidence, Recruiter Agents
│   ├── prompts/                    # Structured system prompts
│   ├── schemas/                    # Pydantic state contracts
│   └── workflows/                  # LangGraph StateGraph pipeline
├── config/                         # MatchingConfig weights & thresholds
├── contracts/                      # Pydantic Data Contracts (Candidate, Job, Match)
├── datasets/                       # Taxonomy, alias dictionary, ground truth dataset
├── db/                             # PostgreSQL DDL schema, SQLAlchemy ORM models, Repositories
├── ingestion/                      # Multi-format document parser & chunker
├── matching/                       # Core matching engine, rules, scorer, gap engine, batch matcher
├── nlp/                            # Normalizer, preprocessing, embeddings, evidence retriever
├── tests/                          # Automated Pytest unit & integration suite
├── vector_store.py                 # pgvector 384-dim vector storage engine
├── main.py                         # Unified FastAPI application entry point
├── verify_member2.py               # Member 2 batch verification script
└── verify_member3.py               # Member 3 database & ingestion verification script
```

---

## Testing & Execution

### 1. Environment & Gemini Configuration (`.env`)
Create `.env` inside `backend/agentic-ai/`:
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
API_KEY=hirelens_secret_key_2026
```

### 2. Run Automated Pytest Suite
```powershell
$env:OPENBLAS_NUM_THREADS="1"; $env:OMP_NUM_THREADS="1"; $env:TESTING="true"; python -m pytest backend/agentic-ai/tests -v
```

### 3. Run Live Supabase Verification Script
```powershell
python backend/agentic-ai/verify_member3.py
```

### 4. Start FastAPI Production Server
```powershell
$env:OPENBLAS_NUM_THREADS="1"; $env:OMP_NUM_THREADS="1"; python -m uvicorn main:app --app-dir backend/agentic-ai --port 8000
```

- **Interactive Swagger UI**: `http://localhost:8000/docs`
- **Health & Metrics Endpoint**: `http://localhost:8000/health`
- **API Documentation**: See [`API_DOCUMENTATION.md`](file:///C:/Users/rahul/.gemini/antigravity/brain/ecb0ed92-eaa8-4327-a6bf-66d746ccceb0/API_DOCUMENTATION.md)

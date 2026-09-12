# HireLens - Multi-Agent Recruitment Intelligence & Matching Engine

HireLens is an enterprise-grade, agentic AI-powered recruitment platform that automates resume ingestion, passage-level evidence grounding, candidate-job matching, and recruiter executive briefings. Built with a **React + Vite** frontend and a **FastAPI + LangGraph** multi-agent backend, HireLens combines vector similarity search (`pgvector`), deterministic weighted scoring rules, and LLM-driven agentic reasoning.

---

## 🏗️ System Architecture

HireLens follows a decoupled microservices architecture with a modern Single-Page Application (SPA) frontend, a high-throughput FastAPI REST backend, a multi-agent orchestration engine powered by LangGraph, and a PostgreSQL database with vector search (`pgvector`).

```mermaid
graph TD
    subgraph "Frontend Layer (React 18 + Vite)"
        UI["Recruiter Dashboard / UI Pages"]
        Upload["Resume Uploader Component"]
        JobForm["Job Builder Form"]
        MatchView["Candidate Match Detail & Trajectory"]
        RankingView["Candidate Ranking Leaderboard"]
    end

    subgraph "API Layer (FastAPI / Uvicorn)"
        Router["FastAPI REST Router (/api/v1)"]
        Auth["Auth & Config Interceptor (X-API-Key / Cors)"]
        Val["Contract Validator & Schema Layer"]
    end

    subgraph "Multi-Agent LangGraph Engine"
        ResumeAgent["1. Resume Extraction Agent"]
        JobAgent["2. Job Structuring Agent"]
        EvidenceAgent["3. Evidence Grounding Agent"]
        GapAgent["4. Skill Gap Categorization Agent"]
        RecruiterAgent["5. Recruiter Briefing Agent"]
    end

    subgraph "Deterministic Rules & Scoring Pipeline"
        Norm["Skill Normalizer & Alias Taxonomy"]
        FeatureEng["Feature Extractor (8 Categories)"]
        Scorer["Scoring Engine (Weighted Formula)"]
        RuleEngine["Mandatory Constraint Checker"]
    end

    subgraph "Storage & Vector Engine"
        VectorEngine["SentenceTransformers (all-MiniLM-L6-v2)"]
        Postgres["PostgreSQL DB (17 ORM Tables)"]
        PgVector["pgvector (384-dim Embeddings)"]
    end

    UI --> Router
    Upload --> Router
    JobForm --> Router
    MatchView --> Router
    RankingView --> Router

    Router --> Auth
    Auth --> Val
    Val --> ResumeAgent
    Val --> JobAgent

    ResumeAgent --> VectorEngine
    VectorEngine --> PgVector
    ResumeAgent --> Postgres

    Router --> RuleEngine
    RuleEngine --> Norm
    Norm --> FeatureEng
    FeatureEng --> Scorer
    Scorer --> EvidenceAgent

    EvidenceAgent --> GapAgent
    GapAgent --> RecruiterAgent
    RecruiterAgent --> Postgres
```

---

## 🤖 Multi-Agent Workflow Engine (LangGraph)

The HireLens backend uses a stateful **LangGraph** execution graph to coordinate specialized AI agents. Each agent operates on a shared state context and logs execution trajectories for auditability.

```mermaid
graph LR
    Start([Raw Resume / Job Input]) --> ResumeAgent["Resume Extraction Agent"]
    ResumeAgent --> JobAgent["Job Structuring Agent"]
    JobAgent --> Rules["Deterministic Feature Engine"]
    Rules --> EvidenceAgent["Evidence Grounding Agent"]
    EvidenceAgent --> GapAgent["Skill Gap Agent"]
    GapAgent --> RecruiterAgent["Recruiter Briefing Agent"]
    RecruiterAgent --> End([Persisted Match & Executive Briefing])
```

### Agent Roles & Responsibilities

1. **Resume Extraction Agent** ([`backend/agentic-ai/agents/resume_agent.py`](file:///d:/Team_SOIT/backend/agentic-ai/agents/resume_agent.py)):
   - Parses unstructured PDF, DOCX, and TXT resume files.
   - Extracts candidate contact info, total experience, experiences, education, skills, and projects into validated Pydantic schemas.
   - Chunks text into passages, generates 384-dimensional vector embeddings via `all-MiniLM-L6-v2`, and stores embeddings in `pgvector`.

2. **Job Structuring Agent** ([`backend/agentic-ai/agents/job_agent.py`](file:///d:/Team_SOIT/backend/agentic-ai/agents/job_agent.py)):
   - Parses raw job postings into structured requirements (`must_have`, `preferred`, `competency`).
   - Identifies mandatory experience thresholds and skill dependencies.

3. **Evidence Grounding Agent** ([`backend/agentic-ai/agents/evidence_agent.py`](file:///d:/Team_SOIT/backend/agentic-ai/agents/evidence_agent.py)):
   - Searches candidate vector passages to verify requirement fulfillment.
   - Assigns requirement statuses (`satisfied`, `partially_supported`, `unsupported`, `contradicted`) with exact page and text citations.

4. **Skill Gap Agent** ([`backend/agentic-ai/agents/skill_gap_agent.py`](file:///d:/Team_SOIT/backend/agentic-ai/agents/skill_gap_agent.py)):
   - Categorizes missing requirements into `critical`, `moderate`, `optional`, or `transferable` skill gaps.
   - Evaluates transferable relationships (e.g., PyTorch ➔ TensorFlow transferability score).

5. **Recruiter Briefing Agent** ([`backend/agentic-ai/agents/recruiter_agent.py`](file:///d:/Team_SOIT/backend/agentic-ai/agents/recruiter_agent.py)):
   - Synthesizes executive recruiter summaries, highlighting top strengths, critical gaps, and tailored interview verification questions.

---

## 🧮 Matching & Scoring Algorithm

HireLens uses a hybrid scoring engine combining deterministic weighted rules, skill hierarchy classification, and semantic vector similarity.

### Weighted Score Distribution

| Category | Weight | Description |
| :--- | :---: | :--- |
| **Must-Have Coverage** | **35%** | Exact, equivalent, or transferable matches for mandatory skills |
| **Preferred Coverage** | **15%** | Matches for secondary / preferred candidate qualifications |
| **Experience Fit** | **15%** | Ratio of candidate total experience months vs required minimum |
| **Role Similarity** | **10%** | Semantic overlap between candidate job titles and target role |
| **Semantic Similarity** | **10%** | Cosine similarity across full resume embedding vector space |
| **Education Match** | **5%** | Degree level matching (Bachelor's, Master's, PhD) |
| **Project Relevance** | **5%** | Alignment between candidate portfolio projects and job domain |
| **Domain Match** | **5%** | Domain expertise alignment (e.g. Backend, CyberSec, Finance) |

### Mandatory Constraint Policy

When a candidate fails a mandatory requirement (e.g. experience is below `min_experience_months` or missing a critical must-have skill):
- `mandatory_pass` is set to `False`.
- `overall_score` is capped at `0.0`.
- Decision is set to `"REJECTED (Mandatory Failed)"`.
- `raw_score_breakdown` is preserved for analytical auditing.

---

## 🗄️ Database Schema & ORM Entities

The system uses SQLAlchemy 2.0 ORM with 17 schema tables supporting PostgreSQL (`pgvector`) and SQLite fallback.

```mermaid
erDiagram
    candidates ||--o{ experiences : "has"
    candidates ||--o{ education : "has"
    candidates ||--o{ candidate_skills : "has"
    candidates ||--o{ documents : "owns"
    candidates ||--o{ matches : "evaluated_in"

    documents ||--o{ document_chunks : "chunked_into"

    jobs ||--o{ job_requirements : "defines"
    jobs ||--o{ matches : "targeted_by"

    matches ||--o{ requirement_assessments : "contains"
    matches ||--o{ evidence_items : "grounds"
    matches ||--o{ gaps : "identifies"
    matches ||--o| recruiter_summaries : "summarized_by"
    matches ||--o{ agent_run_logs : "records"

    skills ||--o{ skill_aliases : "aliased_by"
    skills ||--o{ skill_relationships : "related_to"
```

### Core Entity Tables

- **`candidates`**: Primary candidate profiles, contact information, total experience months, and unmapped metadata.
- **`experiences`**: Candidate work history entries (company, role, duration, start/end dates, description).
- **`education`**: Academic history (degree, field, institution, graduation year).
- **`candidate_skills`**: Parsed candidate skills, confidence ratings, normalized taxonomy names, and evidence text.
- **`documents`**: Uploaded resume files, file hashes (MD5 deduplication), file types, and status.
- **`document_chunks`**: Text passages with page numbers, character offsets, and 384-dimensional `pgvector` embeddings.
- **`jobs`**: Job postings with titles, departments, mandatory/preferred skill lists, and domain descriptors.
- **`job_requirements`**: Granular requirement rules, categories, mandatory flags, and duration constraints.
- **`matches`**: Calculated match records with overall scores, raw scores, decisions, status, and policy versions.
- **`requirement_assessments`**: Passage-level evidence extractions, status (`satisfied`, `partially_supported`), and earned points.
- **`gaps`**: Identified skill deficits categorized by severity with suggested mitigations.
- **`recruiter_summaries`**: Executive summaries, strengths, risks, and interview guidance.
- **`agent_run_logs`**: Full audit log of agent execution steps, input/output summaries, and execution timing.

---

## 🌐 REST API Reference

All backend API endpoints are available under the `/api/v1` prefix.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | System health check and status |
| `GET` | `/api/v1/stats` | Dashboard statistics (candidate counts, job counts, average scores) |
| `POST` | `/api/v1/resumes/upload` | Multi-file resume upload (`.pdf`, `.docx`, `.txt`) with deduplication |
| `GET` | `/api/v1/candidates` | List all ingested candidate profiles |
| `GET` | `/api/v1/candidates/{id}` | Retrieve detailed profile for a specific candidate |
| `GET` | `/api/v1/jobs` | List all active job postings |
| `POST` | `/api/v1/jobs` | Create a new job description with structured requirements |
| `POST` | `/api/v1/matches/run` | Execute the matching engine for a candidate and job |
| `GET` | `/api/v1/matches/{id}` | Fetch match breakdown, assessments, and agent logs (returns `200` `no_match` if unsaved) |
| `GET` | `/api/v1/matches/{job_id}/{candidate_id}` | Fetch match breakdown by job ID and candidate ID |
| `GET` | `/api/v1/ranking` | Rank candidates across jobs sorted by match score |
| `GET` | `/api/v1/ranking/{job_id}` | Rank candidates for a specific job ID |

---

## 💻 Frontend Application Architecture

The frontend is built as a single-page React 18 application with Tailwind CSS and Vite.

### Key Pages & Components

- **Dashboard Page** ([`src/pages/Dashboard.jsx`](file:///d:/Team_SOIT/src/pages/Dashboard.jsx)): High-level metrics, system status overview, and quick action cards.
- **Candidate Database** ([`src/pages/CandidateList.jsx`](file:///d:/Team_SOIT/src/pages/CandidateList.jsx)): Table view of candidates with filtering, search, and direct profile navigation.
- **Candidate Match Detail** ([`src/pages/MatchDetail.jsx`](file:///d:/Team_SOIT/src/pages/MatchDetail.jsx)): Visual breakdown displaying overall score gauge, agent trajectory timeline, category radar breakdown, requirement assessments, and match execution controls.
- **Resume Upload** ([`src/pages/ResumeUpload.jsx`](file:///d:/Team_SOIT/src/pages/ResumeUpload.jsx)): Drag-and-drop file uploader with real-time parsing progress feedback.
- **Job Builder** ([`src/pages/JobBuilder.jsx`](file:///d:/Team_SOIT/src/pages/JobBuilder.jsx)): Form to construct job descriptions and define mandatory constraints.
- **Ranking Leaderboard** ([`src/pages/RankingView.jsx`](file:///d:/Team_SOIT/src/pages/RankingView.jsx)): Job candidate rankings sorted by match scores.
- **System Logs Viewer** ([`src/pages/SystemLogs.jsx`](file:///d:/Team_SOIT/src/pages/SystemLogs.jsx)): Execution log inspector for tracking multi-agent steps.

---

## 🛠️ Real-World Setup & Execution Guide

### Prerequisites
- **Python**: 3.10 or higher
- **Node.js**: v18 or higher (with `npm`)
- **Database**: PostgreSQL (with `pgvector` extension) or SQLite (automatic fallback)

---

### Step 1: Configure Environment Variables (`.env`)

Create or update your `.env` file in the root directory:

```env
# Database Connection (Supabase Cloud PostgreSQL or Local Postgres)
DATABASE_URL=postgresql://postgres.grcihwgasjgofsrlhdox:Msc%4014056%24%24@aws-0-ap-south-1.pooler.supabase.com:5432/postgres

# AI LLM Provider Configuration
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash

# Optional API Key Authentication (Set REQUIRE_AUTH=true for strict API key validation)
REQUIRE_AUTH=false
API_KEY=your_optional_secret_key

# Server & Client Ports
PORT=8000
VITE_API_URL=http://localhost:8000/api/v1
```

---

### Step 2: Start the FastAPI Backend Server

Open a terminal (PowerShell / Command Prompt) and execute:

```powershell
# 1. Set multi-threaded reloader environment variables
$env:OPENBLAS_NUM_THREADS="1"; $env:OMP_NUM_THREADS="1"

# 2. Start Uvicorn backend server
python -m uvicorn main:app --app-dir backend/agentic-ai --reload --port 8000
```

> **Interactive API Docs**: Open `http://localhost:8000/docs` in your browser to view the OpenAPI Swagger documentation.

---

### Step 3: Start the React Frontend Application

Open a second terminal window and execute:

```powershell
# 1. Install frontend packages
npm install

# 2. Launch Vite dev server
npm run dev
```

> **Access Application**: Navigate to `http://localhost:5173`.

---

## 🧪 Running Automated Test Suite

HireLens includes an automated 47-test unit and integration test suite covering vector embeddings, ORM persistence, LangGraph agents, scoring edge cases, and REST API endpoints.

To run the complete test suite:

```powershell
$env:OPENBLAS_NUM_THREADS="1"; $env:OMP_NUM_THREADS="1"; $env:TESTING="true"; python -m pytest backend/agentic-ai/tests -v
```

---

## 📄 License

This repository is maintained for Team SOIT recruitment intelligence system development.
# Member 1 — Agentic AI / LLM / Backend Intelligence Engine

Welcome to the AI brain of the recruitment system for the MIT Hackathon project.

This subsystem provides:
- **Resume Agent**: Converts unstructured resumes into strict `CandidateProfile` Pydantic models.
- **Job Agent**: Converts unstructured job descriptions into machine-readable `JobProfile` specifications with requirement weights (1–10).
- **Skill Gap Agent**: Explains missing skills identified by Member 2's matching engine and discovers transferable skills.
- **Evidence Agent**: Audits candidate experience against job requirements and pulls direct verifiable quotes.
- **Recruiter Agent**: Synthesizes the deterministic match score, breakdown, evidence, and gaps into an actionable recruiter briefing (without ever computing the score itself).
- **LangGraph Orchestrator**: Manages state transitions, parallel processing, and end-to-end execution.
- **FastAPI Endpoints**: REST interface for Member 4's frontend UI and cross-team integration.

---

## 🏗️ Architecture

```text
                    FastAPI (/workflows/run)
                             │
                             ▼
                   LangGraph StateGraph
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
      Resume Agent                       Job Agent
            │                                 │
            ▼                                 ▼
    CandidateProfile                     JobProfile
            │                                 │
            └────────────────┬────────────────┘
                             ▼
                      Matching Engine
                    [Member 2 Contract]
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
             Skill Gap Agent    Evidence Agent
                    │                 │
                    └────────┬────────┘
                             ▼
                      Recruiter Agent
                             │
                             ▼
                    Hiring Recommendation
```

---

## 🚀 Quick Start Guide

### 1. Set Up Virtual Environment

From PowerShell in this directory (`backend/agentic-ai`):

```powershell
# Create virtualenv using Python 3.11
python -m venv venv

# Activate virtualenv
.\venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env`:

```powershell
Copy-Item .env.example .env
```

Edit `.env` to configure your preferred LLM provider:
- `LLM_PROVIDER=openai` (with `OPENAI_API_KEY=...`)
- `LLM_PROVIDER=gemini` (with `GEMINI_API_KEY=...`)
- `LLM_PROVIDER=mock` (works offline out-of-the-box with deterministic mock responses)

---

## 🧪 Running Tests

Verify agents independently:
```powershell
python tests/test_agents.py
```

Verify full end-to-end LangGraph pipeline:
```powershell
python tests/test_pipeline.py
```

---

## 🌐 Running the FastAPI Server

Launch the server with auto-reload:
```powershell
uvicorn main:app --reload --port 8000
```

Open your browser to:
- **Interactive Swagger Docs**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`

---

## 📡 API Endpoints Reference

### 1. Parse Resume
- **Endpoint**: `POST /agents/resume`
- **Body**:
```json
{
  "candidate_id": "C01",
  "text": "Alex Johnson\nSkills: Python, FastAPI..."
}
```

### 2. Parse Job Description
- **Endpoint**: `POST /agents/job`
- **Body**:
```json
{
  "job_id": "J01",
  "text": "Looking for Senior Backend Engineer with 3+ years in Python..."
}
```

### 3. Run Recruitment Workflow (Batch)
- **Endpoint**: `POST /workflows/run`
- **Body**:
```json
{
  "resumes": {
    "C01": "Alex Johnson resume text...",
    "C02": "Sarah Connor resume text..."
  },
  "jobs": {
    "J01": "Senior Backend Engineer JD..."
  }
}
```


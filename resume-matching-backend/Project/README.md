# Resume Matching Backend

A FastAPI backend that scores how well a resume matches a job description,
broken down into four dimensions: **skills**, **experience**, **education**,
and **role**.

## Project Structure

```
Project/
├── app/
│   ├── __init__.py          # FastAPI app factory (create_app)
│   ├── main.py               # uvicorn entrypoint (app.main:app)
│   ├── config.py             # skill vocabulary, education ranks, score weights
│   ├── schemas.py            # Pydantic request/response models
│   ├── routes.py             # API endpoints
│   │
│   ├── preprocessing/
│   │   ├── __init__.py
│   │   ├── text_cleaner.py   # text normalization
│   │   └── extractor.py      # skills / years / education / roles extraction
│   │
│   └── matching/
│       ├── __init__.py
│       ├── skill_matcher.py       # skill overlap scoring
│       ├── experience_matcher.py  # years-of-experience scoring
│       ├── education_matcher.py   # education-level scoring
│       ├── role_matcher.py        # job-title similarity scoring
│       └── aggregator.py          # combines all scores (weighted)
│
├── tests/
│   ├── __init__.py
│   ├── test_matchers.py      # unit tests for matching logic
│   └── test_api.py           # API integration tests
│
├── requirements.txt
└── README.md
```

## How Matching Works

1. **Preprocessing** cleans raw text and extracts structured signals:
   - Skills, matched against a known vocabulary (`app/config.py::KNOWN_SKILLS`)
   - Years of experience, via regex (`"5 years of experience"`, `"3+ yrs"`, etc.)
   - Education level, via keyword matching against a ranked list (high school → PhD)
   - Candidate job-title phrases (e.g. `"senior software engineer"`)

2. **Matching** scores each dimension independently:
   - **Skills**: fraction of job-required skills present in the resume
   - **Experience**: `min(1, resume_years / required_years)`
   - **Education**: `min(1, resume_rank / required_rank)` on the ranked scale
   - **Role**: best similarity (word overlap + fuzzy string match) between
     the target job title and any role phrase found in the resume

3. **Aggregation** combines the four scores into one `overall_score` using
   configurable weights in `app/config.py::MATCH_WEIGHTS` (skills 45%,
   experience 20%, education 15%, role 20% by default).

This is a rule-based, dependency-free implementation designed to be easy to
extend — e.g. swap `KNOWN_SKILLS` for a real taxonomy, or replace a matcher
with an embedding-based semantic similarity model, without touching the
rest of the pipeline.

## Setup

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run the API

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.
Interactive docs: `http://127.0.0.1:8000/docs`.

## API

### `GET /health`
Health check. Returns `{"status": "ok"}`.

### `POST /api/match`

**Request body:**
```json
{
  "resume_text": "Senior Software Engineer with 5 years of experience in Python, Django, PostgreSQL. Bachelor degree in Computer Science.",
  "job_description": "Hiring a Software Engineer with 3+ years experience. Required: Python, Django, PostgreSQL, Docker. Bachelor degree required.",
  "job_title": "Software Engineer"
}
```

`job_title` is optional — if omitted, the matcher tries to infer the target
role from the job description text.

**Response:**
```json
{
  "overall_score": 0.9659,
  "skills": {
    "score": 1.0,
    "matched_skills": ["django", "docker", "postgresql", "python"],
    "missing_skills": [],
    "resume_skills": ["aws", "django", "docker", "postgresql", "python"],
    "job_skills": ["django", "docker", "postgresql", "python"]
  },
  "experience": {
    "score": 1.0,
    "resume_years": 5.0,
    "required_years": 3.0
  },
  "education": {
    "score": 1.0,
    "resume_level": "bachelor",
    "required_level": "bachelor"
  },
  "role": {
    "score": 0.8293,
    "resume_roles": ["senior software engineer"],
    "job_role": "software engineer"
  }
}
```

## Tests

```bash
pytest
```

`tests/test_matchers.py` covers the matching logic in isolation (no web
framework required). `tests/test_api.py` covers the HTTP layer end-to-end
using FastAPI's `TestClient`.

## Extending

- **Add skills**: extend `KNOWN_SKILLS` in `app/config.py`.
- **Add education levels**: extend `EDUCATION_RANKS` in `app/config.py`.
- **Re-weight scoring**: adjust `MATCH_WEIGHTS` in `app/config.py` (must sum to 1.0).
- **Swap in ML-based matching**: each matcher in `app/matching/` returns a
  plain dict with a `score` key — replace the internals of any matcher
  (e.g. `skill_matcher.py`) with an embedding-similarity model without
  changing its public function signature.
- **File uploads (PDF/DOCX resumes)**: add a parsing step before
  `clean_text()` in `app/preprocessing/` and pass the extracted text into
  the existing pipeline unchanged.

# HireLens — Multi-Agent Recruitment Intelligence Backend

HireLens is an explainable stateful multi-agent recruitment intelligence platform built with FastAPI, LangGraph, LangChain, spaCy, sentence-transformers, and PostgreSQL/pgvector.

## Member 2 — Data Science / NLP / Matching Engine

Member 2 owns the intelligence, semantic understanding, skill normalization, 5-tier matching hierarchy, 100-point scoring model, skill gap analysis, batch matching, and quantitative evaluation layer.

### Directory Structure

```
backend/agentic-ai/
├── config/
│   └── matching_config.py          # Validated MatchingConfig with weights & thresholds
├── contracts/
│   ├── candidate.py                # CandidateProfile Pydantic schema
│   ├── job.py                      # JobProfile & JobRequirement Pydantic schema
│   └── match.py                    # MatchResult & SkillGaps Pydantic schema
├── datasets/
│   ├── skills.csv                  # Canonical skill taxonomy
│   ├── aliases.csv                 # Skill alias dictionary
│   ├── skill_relationships.csv     # Technology transferability matrix
│   ├── education_levels.csv        # Degree level hierarchy mapping
│   └── ground_truth.csv            # 10x3 Benchmark evaluation ground truth
├── nlp/
│   ├── aliases.py                  # Alias lookup service
│   ├── preprocessing.py            # spaCy text cleaning & date math
│   ├── skill_normalizer.py         # 3-tier normalization (alias + fuzzy + canonical)
│   ├── skill_relationships.py      # Transferability & relationship lookup
│   ├── role_normalizer.py          # Canonical role normalization
│   ├── embeddings.py               # Singleton SentenceTransformer with hash caching
│   └── similarity.py               # Cosine similarity calculation
├── matching/
│   ├── feature_filter.py           # PII-Safe feature filtering & sanitization
│   ├── rules.py                    # 5-tier matching hierarchy & mandatory checks
│   ├── feature_engineering.py      # 8-feature candidate-job matrix computation
│   ├── scorer.py                   # 100-point weighted score calculator
│   ├── gap_engine.py               # Critical, moderate, optional gap categorization
│   ├── ranking.py                  # Candidate ranking engine
│   ├── batch_matcher.py            # Isolated batch matching (10x3 = 30 matches)
│   ├── metrics.py                  # Precision@K, Recall@K, NDCG@K, Spearman correlation
│   ├── evaluation.py               # Ground truth benchmark experiment runner
│   └── pipeline.py                 # Unified single match entry point
├── notebooks/
│   └── evaluation.ipynb            # Jupyter evaluation notebook
├── tests/                          # 11 Unit & Integration test modules
│   ├── test_normalizer.py
│   ├── test_relationships.py
│   ├── test_similarity.py
│   ├── test_rules.py
│   ├── test_features.py
│   ├── test_scorer.py
│   ├── test_gap_engine.py
│   ├── test_ranking.py
│   ├── test_batch_matcher.py
│   ├── test_pipeline.py
│   └── test_edge_cases.py
├── main.py                         # FastAPI web server entry point
└── verify_member2.py               # Verification script for 10x3 demo
```

## Testing & Execution Instructions

### 1. Run Unit Tests via Pytest
From the repository root (`d:\Team_SOIT`):
```bash
python -m pytest backend/agentic-ai/tests -v
```

### 2. Run 10x3 Demo Verification Script
```bash
python backend/agentic-ai/verify_member2.py
```

### 3. Launch FastAPI Development Server
```bash
python backend/agentic-ai/main.py
```
Or with Uvicorn:
```bash
uvicorn backend.agentic-ai.main:app --reload
```

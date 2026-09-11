-- HireLens Database DDL Schema
-- Support PostgreSQL with pgvector extension and ON DELETE CASCADE foreign keys.

CREATE EXTENSION IF NOT EXISTS vector;

-- 1. Candidates Table
CREATE TABLE IF NOT EXISTS candidates (
    candidate_id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255) DEFAULT 'Anonymous Candidate',
    email VARCHAR(255),
    phone VARCHAR(50),
    total_experience_months INTEGER DEFAULT 0,
    certifications JSONB DEFAULT '[]'::jsonb,
    projects JSONB DEFAULT '[]'::jsonb,
    domains JSONB DEFAULT '[]'::jsonb,
    unmapped_fields JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Experiences Table
CREATE TABLE IF NOT EXISTS experiences (
    id SERIAL PRIMARY KEY,
    candidate_id VARCHAR(100) NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    role VARCHAR(255) NOT NULL,
    company VARCHAR(255),
    duration_months INTEGER DEFAULT 0,
    start_date VARCHAR(50),
    end_date VARCHAR(50),
    description TEXT
);

-- 3. Education Table
CREATE TABLE IF NOT EXISTS education (
    id SERIAL PRIMARY KEY,
    candidate_id VARCHAR(100) NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    degree VARCHAR(255) NOT NULL,
    field VARCHAR(255),
    institution VARCHAR(255),
    graduation_year INTEGER
);

-- 4. Candidate Skills Table
CREATE TABLE IF NOT EXISTS candidate_skills (
    id SERIAL PRIMARY KEY,
    candidate_id VARCHAR(100) NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    raw_skill VARCHAR(255) NOT NULL,
    normalized_skill VARCHAR(255),
    confidence DOUBLE PRECISION DEFAULT 1.0,
    years_experience DOUBLE PRECISION,
    evidence TEXT,
    page INTEGER
);

-- 5. Documents Table
CREATE TABLE IF NOT EXISTS documents (
    id VARCHAR(100) PRIMARY KEY,
    candidate_id VARCHAR(100) NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size INTEGER NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    raw_content TEXT,
    status VARCHAR(50) DEFAULT 'processed',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_candidate_file_hash UNIQUE (candidate_id, file_hash)
);

-- 6. Document Chunks Table (Vector Storage)
CREATE TABLE IF NOT EXISTS document_chunks (
    id VARCHAR(100) PRIMARY KEY,
    document_id VARCHAR(100) NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    candidate_id VARCHAR(100) NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    page_number INTEGER DEFAULT 1,
    start_char INTEGER DEFAULT 0,
    end_char INTEGER DEFAULT 0,
    section_title VARCHAR(255),
    embedding vector(384),
    embedding_model VARCHAR(100) DEFAULT 'all-MiniLM-L6-v2',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_chunks_candidate ON document_chunks(candidate_id);
CREATE INDEX IF NOT EXISTS idx_chunks_document ON document_chunks(document_id);

-- 7. Jobs Table
CREATE TABLE IF NOT EXISTS jobs (
    job_id VARCHAR(100) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    department VARCHAR(255) DEFAULT 'Engineering',
    status VARCHAR(50) DEFAULT 'Active',
    description TEXT,
    domain JSONB DEFAULT '[]'::jsonb,
    min_experience_months INTEGER DEFAULT 0,
    must_have_skills JSONB DEFAULT '[]'::jsonb,
    preferred_skills JSONB DEFAULT '[]'::jsonb,
    education_requirements JSONB DEFAULT '[]'::jsonb,
    certifications JSONB DEFAULT '[]'::jsonb,
    responsibilities JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 8. Job Requirements Table
CREATE TABLE IF NOT EXISTS job_requirements (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(100) NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    requirement_id VARCHAR(100),
    description TEXT NOT NULL,
    skill VARCHAR(255),
    category VARCHAR(50) DEFAULT 'competency',
    importance VARCHAR(50) DEFAULT 'must_have',
    mandatory BOOLEAN DEFAULT FALSE,
    weight DOUBLE PRECISION DEFAULT 10.0,
    minimum_duration_months INTEGER DEFAULT 0
);

-- 9. Skills Taxonomy Table
CREATE TABLE IF NOT EXISTS skills (
    id SERIAL PRIMARY KEY,
    canonical_name VARCHAR(255) UNIQUE NOT NULL,
    category VARCHAR(100) DEFAULT 'general'
);

-- 10. Skill Aliases Table
CREATE TABLE IF NOT EXISTS skill_aliases (
    id SERIAL PRIMARY KEY,
    alias_name VARCHAR(255) UNIQUE NOT NULL,
    canonical_name VARCHAR(255) NOT NULL
);

-- 11. Skill Relationships Table
CREATE TABLE IF NOT EXISTS skill_relationships (
    id SERIAL PRIMARY KEY,
    source_skill VARCHAR(255) NOT NULL,
    target_skill VARCHAR(255) NOT NULL,
    relationship VARCHAR(50) NOT NULL,
    transferability DOUBLE PRECISION NOT NULL,
    CONSTRAINT uq_skill_pair UNIQUE (source_skill, target_skill)
);

-- 12. Matches Table
CREATE TABLE IF NOT EXISTS matches (
    match_id VARCHAR(100) PRIMARY KEY,
    job_id VARCHAR(100) NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    candidate_id VARCHAR(100) NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    overall_score DOUBLE PRECISION NOT NULL,
    raw_score DOUBLE PRECISION NOT NULL,
    overall_status VARCHAR(50) NOT NULL,
    decision VARCHAR(50) NOT NULL,
    evidence_coverage DOUBLE PRECISION DEFAULT 0.0,
    raw_score_breakdown JSONB DEFAULT '{}'::jsonb,
    uncertainty_flags JSONB DEFAULT '[]'::jsonb,
    embedding_model VARCHAR(100) DEFAULT 'all-MiniLM-L6-v2',
    scoring_policy_version VARCHAR(50) DEFAULT 'v1.0',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_job_candidate_match UNIQUE (job_id, candidate_id)
);

-- 13. Requirement Assessments Table
CREATE TABLE IF NOT EXISTS requirement_assessments (
    id SERIAL PRIMARY KEY,
    match_id VARCHAR(100) NOT NULL REFERENCES matches(match_id) ON DELETE CASCADE,
    requirement_id VARCHAR(100),
    requirement_description TEXT,
    req_category VARCHAR(50),
    req_importance VARCHAR(50),
    candidate_evidence TEXT,
    evidence_passage TEXT,
    source_page INTEGER,
    evidence_confidence DOUBLE PRECISION,
    status VARCHAR(50),
    weight DOUBLE PRECISION,
    earned_score DOUBLE PRECISION,
    max_score DOUBLE PRECISION,
    score_ratio DOUBLE PRECISION
);

-- 14. Evidence Items Table
CREATE TABLE IF NOT EXISTS evidence_items (
    id SERIAL PRIMARY KEY,
    match_id VARCHAR(100) NOT NULL REFERENCES matches(match_id) ON DELETE CASCADE,
    requirement_id VARCHAR(100),
    candidate_skill VARCHAR(255),
    matched_text TEXT,
    evidence_passage TEXT,
    page_number INTEGER,
    confidence DOUBLE PRECISION
);

-- 15. Gaps Table
CREATE TABLE IF NOT EXISTS gaps (
    id SERIAL PRIMARY KEY,
    match_id VARCHAR(100) NOT NULL REFERENCES matches(match_id) ON DELETE CASCADE,
    skill VARCHAR(255) NOT NULL,
    gap_type VARCHAR(50) NOT NULL,
    impact VARCHAR(50),
    severity VARCHAR(50),
    mitigations JSONB DEFAULT '[]'::jsonb
);

-- 16. Recruiter Summaries Table
CREATE TABLE IF NOT EXISTS recruiter_summaries (
    id SERIAL PRIMARY KEY,
    match_id VARCHAR(100) NOT NULL REFERENCES matches(match_id) ON DELETE CASCADE,
    candidate_id VARCHAR(100) NOT NULL,
    job_id VARCHAR(100) NOT NULL,
    summary_text TEXT NOT NULL,
    key_strengths JSONB DEFAULT '[]'::jsonb,
    key_gaps JSONB DEFAULT '[]'::jsonb,
    recommendation VARCHAR(100)
);

-- 17. Agent Run Logs Table
CREATE TABLE IF NOT EXISTS agent_run_logs (
    id SERIAL PRIMARY KEY,
    match_id VARCHAR(100) NOT NULL REFERENCES matches(match_id) ON DELETE CASCADE,
    agent_name VARCHAR(100) NOT NULL,
    step_index INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'success',
    input_summary TEXT,
    output_summary TEXT,
    duration_ms INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

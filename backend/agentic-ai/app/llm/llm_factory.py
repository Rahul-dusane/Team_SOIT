"""Centralized LLM Factory supporting multiple providers with fallback capability."""

import os
from typing import Any, Optional, Type
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_core.runnables import Runnable

load_dotenv()


class MockStructuredLLM(Runnable):
    """Mock structured LLM for offline testing or when no API key is configured."""
    
    def __init__(self, schema: Type[BaseModel]):
        self.schema = schema

    def invoke(self, input_dict: Any, config: Optional[Any] = None, **kwargs) -> BaseModel:
        """Returns dummy structured data adhering strictly to the required Pydantic schema."""
        if not isinstance(input_dict, dict):
            input_dict = {}
        schema_name = self.schema.__name__
        
        if schema_name == "CandidateProfile":
            candidate_id = "C01"
            if isinstance(input_dict, dict) and "candidate_id" in input_dict:
                candidate_id = input_dict["candidate_id"]
            return self.schema(
                candidate_id=candidate_id,
                name="Alex Johnson",
                email="alex.johnson@example.com",
                summary="Full-stack backend developer with 4 years experience building scalable APIs.",
                skills=[
                    {"name": "Python", "confidence": 0.98, "evidence": "4 years developing microservices in Python"},
                    {"name": "FastAPI", "confidence": 0.95, "evidence": "Built high-throughput REST APIs using FastAPI"},
                    {"name": "PostgreSQL", "confidence": 0.90, "evidence": "Designed schema and query optimization for PostgreSQL"},
                    {"name": "Docker", "confidence": 0.85, "evidence": "Containerized multi-service applications"},
                    {"name": "AWS", "confidence": 0.75, "evidence": "Deployed services to AWS ECS and S3"}
                ],
                experience=[
                    {
                        "company": "TechCorp",
                        "role": "Backend Software Engineer",
                        "duration_months": 36,
                        "description": "Architected REST APIs, implemented caching, and handled database migrations.",
                        "technologies": ["Python", "FastAPI", "PostgreSQL", "Docker"]
                    },
                    {
                        "company": "StartupX",
                        "role": "Junior Developer",
                        "duration_months": 12,
                        "description": "Built automated data ingestion pipelines.",
                        "technologies": ["Python", "SQLite"]
                    }
                ],
                total_experience_months=48,
                education=[
                    {
                        "degree": "B.S.",
                        "field": "Computer Science",
                        "institution": "State University",
                        "graduation_year": 2021
                    }
                ],
                projects=["Distributed Rate Limiter in FastAPI", "E-commerce Catalog Service"],
                certifications=["AWS Certified Solutions Architect Associate"],
                domains=["Backend Engineering", "Cloud Services"]
            )
            
        elif schema_name == "JobProfile":
            job_id = "J01"
            if isinstance(input_dict, dict) and "job_id" in input_dict:
                job_id = input_dict["job_id"]
            return self.schema(
                job_id=job_id,
                title="Senior Backend Engineer (Python / FastAPI)",
                requirements=[
                    {"requirement": "Python", "requirement_type": "MUST_HAVE", "importance": "CRITICAL", "weight": 10.0},
                    {"requirement": "FastAPI", "requirement_type": "MUST_HAVE", "importance": "CRITICAL", "weight": 9.5},
                    {"requirement": "PostgreSQL", "requirement_type": "MUST_HAVE", "importance": "HIGH", "weight": 9.0},
                    {"requirement": "Kubernetes", "requirement_type": "MUST_HAVE", "importance": "HIGH", "weight": 8.5},
                    {"requirement": "Docker", "requirement_type": "PREFERRED", "importance": "HIGH", "weight": 7.0},
                    {"requirement": "AWS", "requirement_type": "PREFERRED", "importance": "MEDIUM", "weight": 6.0}
                ],
                must_have_skills=["Python", "FastAPI", "PostgreSQL", "Kubernetes"],
                preferred_skills=["Docker", "AWS"],
                min_experience_months=36,
                education_requirements=["Bachelor's degree in CS or equivalent"],
                responsibilities=[
                    "Design and implement high-performance backend microservices",
                    "Maintain database integrity and performance tuning",
                    "Deploy containerized workloads to cloud clusters"
                ],
                domain=["Backend", "Cloud Infrastructure"]
            )

        elif schema_name == "SkillGapAnalysis":
            cid = input_dict.get("candidate_id", "C01") if isinstance(input_dict, dict) else "C01"
            jid = input_dict.get("job_id", "J01") if isinstance(input_dict, dict) else "J01"
            return self.schema(
                candidate_id=cid,
                job_id=jid,
                critical_gaps=["Kubernetes"],
                moderate_gaps=[],
                transferable_skills=[
                    {
                        "candidate_skill": "Docker",
                        "target_skill": "Kubernetes",
                        "relevance_rationale": "Strong containerization foundation with Docker provides immediate familiarity with container deployment fundamentals."
                    }
                ],
                upskilling_recommendations=["Hands-on deployment practice with Kubernetes pods, services, and Helm charts."],
                gap_summary="Candidate satisfies all core application development and database needs but lacks production Kubernetes cluster management experience."
            )

        elif schema_name == "EvidenceReport":
            cid = input_dict.get("candidate_id", "C01") if isinstance(input_dict, dict) else "C01"
            jid = input_dict.get("job_id", "J01") if isinstance(input_dict, dict) else "J01"
            return self.schema(
                candidate_id=cid,
                job_id=jid,
                items=[
                    {
                        "requirement": "Python",
                        "status": "VERIFIED",
                        "quote": "4 years developing microservices in Python",
                        "context_source": "TechCorp Experience",
                        "confidence": 0.98
                    },
                    {
                        "requirement": "FastAPI",
                        "status": "VERIFIED",
                        "quote": "Built high-throughput REST APIs using FastAPI",
                        "context_source": "TechCorp Experience & Projects",
                        "confidence": 0.95
                    },
                    {
                        "requirement": "PostgreSQL",
                        "status": "VERIFIED",
                        "quote": "Designed schema and query optimization for PostgreSQL",
                        "context_source": "TechCorp Experience",
                        "confidence": 0.90
                    },
                    {
                        "requirement": "Kubernetes",
                        "status": "NOT_FOUND",
                        "quote": None,
                        "context_source": None,
                        "confidence": 0.0
                    }
                ]
            )

        elif schema_name == "RecruiterSummary":
            cid = input_dict.get("candidate_id", "C01") if isinstance(input_dict, dict) else "C01"
            jid = input_dict.get("job_id", "J01") if isinstance(input_dict, dict) else "J01"
            score = input_dict.get("overall_score", 85.0) if isinstance(input_dict, dict) else 85.0
            return self.schema(
                candidate_id=cid,
                job_id=jid,
                overall_score=score,
                recommendation="POTENTIAL_MATCH",
                headline="Strong backend Python/FastAPI candidate with proven database expertise, missing only Kubernetes.",
                summary="Candidate has strong backend experience with Python and FastAPI, exceeds experience threshold, but lacks Kubernetes.",
                strengths=[
                    "48 months of relevant backend experience (exceeds 36-month minimum requirement)",
                    "Direct daily experience architecting REST APIs with FastAPI and PostgreSQL",
                    "Strong container background with Docker"
                ],
                concerns=[
                    "No demonstrated production experience with Kubernetes container orchestration"
                ],
                interview_focus=[
                    "Assess architecture principles for distributed systems",
                    "Evaluate container orchestration willingness and fundamentals (Docker vs K8s)",
                    "Deep dive into PostgreSQL query optimization and indexing strategies"
                ],
                suggested_role_level="Mid-to-Senior Backend Engineer"
            )

        # Fallback default instantiation
        return self.schema.model_construct()


class MockLLM:
    """Wrapper that mimics BaseChatModel with .with_structured_output()."""
    def with_structured_output(self, schema: Type[BaseModel]):
        return MockStructuredLLM(schema)


def get_llm(temperature: float = 0.0, force_mock: bool = False):
    """
    Returns an initialized LLM with structured output support.
    Automatically falls back to MockLLM if no API key is detected.
    """
    if force_mock:
        return MockLLM()

    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    openai_key = os.getenv("OPENAI_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")

    if provider == "openai":
        if not openai_key or openai_key.startswith("your_"):
            # Graceful fallback so program runs out-of-the-box
            return MockLLM()
        try:
            from langchain_openai import ChatOpenAI
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            return ChatOpenAI(model=model, temperature=temperature, api_key=openai_key)
        except Exception:
            return MockLLM()

    elif provider == "gemini":
        if not gemini_key or gemini_key.startswith("your_"):
            return MockLLM()
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
            return ChatGoogleGenerativeAI(model=model, temperature=temperature, google_api_key=gemini_key)
        except Exception:
            return MockLLM()

    # Default fallback
    return MockLLM()


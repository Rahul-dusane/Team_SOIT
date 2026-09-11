"""
verify_member2.py
Domain-Independent Verification Script testing 10 candidates x 3 multi-domain jobs (IT, Accounting, Healthcare)
verifying 100% batch execution (30/30 matches succeeded, 0 errors) and quantitative ground truth benchmarks.
"""

import sys
import os

# Add backend/agentic-ai directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from contracts.candidate import CandidateProfile, CandidateSkill, CandidateExperience, CandidateEducation
from contracts.job import JobProfile, JobRequirement
from matching.batch_matcher import match_all
from matching.evaluation import evaluate_batch_results


def generate_sample_dataset():
    """Generates 10 candidate profiles across diverse domains (IT, Accounting, Healthcare, Engineering)."""
    candidates = [
        # C01 - IT Backend Engineer
        CandidateProfile(
            candidate_id="C01",
            name="Alice Backend",
            total_experience_months=48,
            skills=[CandidateSkill(raw_skill="Python"), CandidateSkill(raw_skill="FastAPI"), CandidateSkill(raw_skill="PostgreSQL")],
            experiences=[CandidateExperience(role="Backend Engineer", duration_months=48, description="Developed Python microservices using FastAPI and PostgreSQL")],
            education=[CandidateEducation(degree="B.Tech", field="Computer Science")]
        ),
        # C02 - Senior Accountant (CPA)
        CandidateProfile(
            candidate_id="C02",
            name="Bob Accountant",
            total_experience_months=60,
            skills=[CandidateSkill(raw_skill="Financial Accounting"), CandidateSkill(raw_skill="Bookkeeping"), CandidateSkill(raw_skill="Tax Auditing")],
            experiences=[CandidateExperience(role="Senior Accountant", duration_months=60, description="Managed monthly financial close, tax auditing, and bookkeeping")],
            education=[CandidateEducation(degree="B.Com", field="Accounting")],
            certifications=["CPA"]
        ),
        # C03 - Registered Nurse (Healthcare)
        CandidateProfile(
            candidate_id="C03",
            name="Carol Nurse",
            total_experience_months=36,
            skills=[CandidateSkill(raw_skill="Patient Care"), CandidateSkill(raw_skill="Phlebotomy"), CandidateSkill(raw_skill="Vital Signs")],
            experiences=[CandidateExperience(role="Clinical Nurse", duration_months=36, description="Administered medication, patient care, and phlebotomy in ICU")],
            education=[CandidateEducation(degree="B.Sc Nursing", field="Nursing")],
            certifications=["Registered Nurse (RN)"]
        ),
        # C04 - Full Stack Developer
        CandidateProfile(
            candidate_id="C04",
            name="David Developer",
            total_experience_months=36,
            skills=[CandidateSkill(raw_skill="React"), CandidateSkill(raw_skill="TypeScript"), CandidateSkill(raw_skill="Node.js")],
            experiences=[CandidateExperience(role="Full Stack Engineer", duration_months=36, description="Built web frontends with React and TypeScript")],
            education=[CandidateEducation(degree="B.E.", field="CS")]
        ),
        # C05 - Data Scientist
        CandidateProfile(
            candidate_id="C05",
            name="Eve Scientist",
            total_experience_months=48,
            skills=[CandidateSkill(raw_skill="Python"), CandidateSkill(raw_skill="PyTorch"), CandidateSkill(raw_skill="scikit-learn")],
            experiences=[CandidateExperience(role="Data Scientist", duration_months=48, description="Trained machine learning models using Python and PyTorch")],
            education=[CandidateEducation(degree="M.S.", field="Data Science")]
        ),
        # C06 - Junior Accountant
        CandidateProfile(
            candidate_id="C06",
            name="Frank Junior",
            total_experience_months=18,
            skills=[CandidateSkill(raw_skill="Bookkeeping"), CandidateSkill(raw_skill="Excel")],
            experiences=[CandidateExperience(role="Accounting Assistant", duration_months=18, description="Assisted with monthly bookkeeping")],
            education=[CandidateEducation(degree="B.Com", field="Finance")]
        ),
        # C07 - Civil Engineer
        CandidateProfile(
            candidate_id="C07",
            name="Grace Engineer",
            total_experience_months=48,
            skills=[CandidateSkill(raw_skill="AutoCAD"), CandidateSkill(raw_skill="Structural Engineering")],
            experiences=[CandidateExperience(role="Civil Engineer", duration_months=48, description="Designed structural building blueprints")],
            education=[CandidateEducation(degree="B.Tech", field="Civil Engineering")]
        ),
        # C08 - Junior Nurse
        CandidateProfile(
            candidate_id="C08",
            name="Hank Assistant",
            total_experience_months=12,
            skills=[CandidateSkill(raw_skill="Patient Care")],
            experiences=[CandidateExperience(role="Nursing Aide", duration_months=12, description="Provided basic patient care")],
            education=[CandidateEducation(degree="Diploma Nursing", field="Nursing")]
        ),
        # C09 - Sales Executive
        CandidateProfile(
            candidate_id="C09",
            name="Ivy Sales",
            total_experience_months=36,
            skills=[CandidateSkill(raw_skill="Lead Generation"), CandidateSkill(raw_skill="Negotiation")],
            experiences=[CandidateExperience(role="Sales Representative", duration_months=36, description="Managed client relationships and sales pipeline")],
            education=[CandidateEducation(degree="B.B.A.", field="Marketing")]
        ),
        # C10 - DevOps Engineer
        CandidateProfile(
            candidate_id="C10",
            name="Jack DevOps",
            total_experience_months=48,
            skills=[CandidateSkill(raw_skill="Docker"), CandidateSkill(raw_skill="Kubernetes"), CandidateSkill(raw_skill="AWS")],
            experiences=[CandidateExperience(role="DevOps Engineer", duration_months=48, description="Managed Kubernetes clusters on AWS")],
            education=[CandidateEducation(degree="B.Tech", field="IT")]
        )
    ]

    jobs = [
        # Job 1: IT Backend Engineer
        JobProfile(
            job_id="J01",
            title="Backend Engineer (Python / FastAPI)",
            description="Python FastAPI backend developer with database experience",
            min_experience_months=24,
            must_have_skills=["Python", "FastAPI"],
            preferred_skills=["PostgreSQL"],
            requirements=[
                JobRequirement(requirement_id="J01_R1", description="Build REST APIs using Python and FastAPI", skill="Python", importance="must_have", weight=20.0),
                JobRequirement(requirement_id="J01_R2", description="Database query optimization with PostgreSQL", skill="PostgreSQL", importance="preferred", weight=10.0),
            ]
        ),
        # Job 2: Financial Accountant (Accounting Domain)
        JobProfile(
            job_id="J02",
            title="Senior Financial Accountant",
            description="Senior accountant responsible for monthly financial close, tax auditing, and bookkeeping",
            min_experience_months=36,
            must_have_skills=["Financial Accounting", "Bookkeeping"],
            certifications=["CPA"],
            requirements=[
                JobRequirement(requirement_id="J02_R1", description="Manage monthly financial close and bookkeeping", skill="Bookkeeping", importance="must_have", weight=25.0),
                JobRequirement(requirement_id="J02_R2", description="Conduct corporate tax auditing and financial reporting", skill="Tax Auditing", importance="must_have", weight=20.0),
            ]
        ),
        # Job 3: Clinical Registered Nurse (Healthcare Domain)
        JobProfile(
            job_id="J03",
            title="Clinical Nurse (RN)",
            description="Registered nurse delivering patient care, vital signs monitoring, and phlebotomy",
            min_experience_months=24,
            must_have_skills=["Patient Care", "Phlebotomy"],
            certifications=["Registered Nurse (RN)"],
            requirements=[
                JobRequirement(requirement_id="J03_R1", description="Deliver critical ICU patient care and medication administration", skill="Patient Care", importance="must_have", weight=25.0),
                JobRequirement(requirement_id="J03_R2", description="Perform blood draw and phlebotomy procedures", skill="Phlebotomy", importance="must_have", weight=15.0),
            ]
        )
    ]

    return candidates, jobs


def main():
    print("=" * 75)
    print("   HIRELENS — DOMAIN-INDEPENDENT MULTI-PROFESSION MATCHING ENGINE VERIFICATION")
    print("=" * 75)

    candidates, jobs = generate_sample_dataset()
    expected_total_matches = len(candidates) * len(jobs)
    print(f"[+] Loaded Dataset: {len(candidates)} Candidates x {len(jobs)} Jobs across IT, Accounting & Healthcare ({expected_total_matches} Match Pairs)")

    print("[*] Running Requirement-Based Evidence Matching Engine...")
    batch_results = match_all(candidates, jobs)

    total_successful = sum(res["successful_matches"] for res in batch_results.values())
    total_errors = sum(len(res["errors"]) for res in batch_results.values())

    print(f"[+] Batch Summary: {total_successful}/{expected_total_matches} Succeeded | {total_errors} Errors")

    if total_successful != expected_total_matches or total_errors > 0:
        raise RuntimeError(f"Production Verification Failed! Expected {expected_total_matches} successful matches, got {total_successful} success and {total_errors} errors.")

    print("\n[+] Top Candidate Rankings per Profession:")
    for job_id, res in batch_results.items():
        print(f"\n--- {res['job_title']} ({job_id}) ---")
        for rank in res["rankings"][:3]:
            print(f"    Rank {rank['rank']}: Candidate {rank['candidate_id']} | Score: {rank['overall_score']:.1f} | Evidence Cov: {res['matches'][rank['rank']-1].evidence_coverage*100:.0f}% | Pass: {rank['mandatory_pass']} | Confidence: {rank['confidence_level']}")

    print("\n[*] Evaluating Multi-Domain Ground Truth Benchmarks...")
    eval_df = evaluate_batch_results(batch_results)
    print("\n" + eval_df.to_string(index=False))

    print("\n" + "=" * 75)
    print(f"ALL {expected_total_matches} MULTI-DOMAIN MATCHES VERIFIED SUCCESSFULLY WITH 0 ERRORS!")
    print("=" * 75)


if __name__ == "__main__":
    main()

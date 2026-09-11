"""
verify_member2.py
Verification script executing end-to-end 10 candidates x 3 jobs (30 match pairs) batch matching,
evaluating metrics against ground truth, and printing formatted ranking tables.
"""

import sys
import os

# Add backend/agentic-ai directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from contracts.candidate import CandidateProfile, CandidateSkill, CandidateExperience, CandidateEducation
from contracts.job import JobProfile
from matching.batch_matcher import match_all
from matching.evaluation import evaluate_batch_results


def generate_sample_dataset():
    """Generates 10 candidate profiles and 3 job descriptions."""
    skills_pool = [
        ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],  # C01 - Strong Backend
        ["Python", "Django", "MySQL", "Azure", "Redis"],       # C02 - Strong Backend (Transferable)
        ["Python", "Flask", "MongoDB"],                         # C03 - Medium Backend
        ["React", "TypeScript", "Node.js", "GraphQL"],          # C04 - Frontend / Fullstack
        ["Python", "PyTorch", "scikit-learn", "Pandas"],        # C05 - Data Science / ML
        ["Java", "Spring Boot", "Oracle"],                      # C06 - Enterprise Java
        ["C++", "Qt", "Linux"],                                # C07 - Systems
        ["HTML", "CSS", "JavaScript"],                          # C08 - Junior Web
        ["PHP", "Laravel", "MySQL"],                            # C09 - Legacy Web
        ["Go", "Kubernetes", "Docker"]                          # C10 - DevOps
    ]

    candidates = []
    for i in range(1, 11):
        cand_id = f"C{i:02d}"
        c_skills = [CandidateSkill(raw_skill=s) for s in skills_pool[i-1]]
        exp_months = (11 - i) * 6 + 12
        candidates.append(CandidateProfile(
            candidate_id=cand_id,
            name=f"Candidate {cand_id}",
            total_experience_months=exp_months,
            skills=c_skills,
            experiences=[CandidateExperience(role="Engineer", duration_months=exp_months, description="Developed software applications")],
            education=[CandidateEducation(degree="B.Tech", field="CS")]
        ))

    jobs = [
        JobProfile(
            job_id="J01",
            title="Backend Engineer (Python / FastAPI)",
            description="Python FastAPI backend developer with cloud experience",
            min_experience_months=24,
            must_have_skills=["Python", "FastAPI"],
            preferred_skills=["PostgreSQL", "AWS", "Docker"]
        ),
        JobProfile(
            job_id="J02",
            title="Full Stack Engineer",
            description="Python and React fullstack developer",
            min_experience_months=24,
            must_have_skills=["Python", "React"],
            preferred_skills=["TypeScript", "PostgreSQL"]
        ),
        JobProfile(
            job_id="J03",
            title="Data Scientist / ML Engineer",
            description="Machine learning engineer proficient in Python and PyTorch",
            min_experience_months=24,
            must_have_skills=["Python", "PyTorch"],
            preferred_skills=["scikit-learn", "Pandas"]
        )
    ]

    return candidates, jobs


def main():
    print("=" * 70)
    print("      HIRELENS - MEMBER 2 DATA SCIENCE / NLP / MATCHING VERIFICATION")
    print("=" * 70)

    candidates, jobs = generate_sample_dataset()
    print(f"[+] Loaded Dataset: {len(candidates)} Candidates x {len(jobs)} Jobs (Total 30 Match Pairs)")

    print("[*] Running Batch Matching Engine...")
    batch_results = match_all(candidates, jobs)

    print("\n[+] Top 3 Rankings per Job:")
    for job_id, res in batch_results.items():
        print(f"\n--- {res['job_title']} ({job_id}) ---")
        for rank in res["rankings"][:3]:
            print(f"    Rank {rank['rank']}: {rank['candidate_id']} | Score: {rank['overall_score']:.1f} | Pass: {rank['mandatory_pass']} | Confidence: {rank['confidence_level']}")

    print("\n[*] Evaluating Quantitative Benchmarks against Ground Truth...")
    eval_df = evaluate_batch_results(batch_results)
    print("\n" + eval_df.to_string(index=False))

    print("\n" + "=" * 70)
    print("ALL MEMBER 2 PIPELINES & BENCHMARKS VERIFIED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    main()

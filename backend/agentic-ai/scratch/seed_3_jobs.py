"""
seed_3_jobs.py
Seeds 3 distinct, domain-diverse job profiles into the HireLens database.
"""

import os
import sys

backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from db.connection import SessionLocal
from db.repositories import JobRepository
from contracts.job import JobProfile, JobRequirement

def seed_jobs():
    db = SessionLocal()
    job_repo = JobRepository(db)

    # Job 1: Engineering & IT Domain
    job1 = JobProfile(
        job_id="JOB_ENGINEERING_01",
        title="Senior FastAPI Backend Developer",
        description="Architect, build, and maintain high-throughput backend microservices and REST APIs using Python, FastAPI, and PostgreSQL.",
        domain=["Engineering & IT"],
        min_experience_months=0,
        must_have_skills=["Python", "FastAPI", "PostgreSQL", "REST API"],
        preferred_skills=["Docker", "AWS", "Kubernetes"],
        education_requirements=["Bachelor's degree in Computer Science or equivalent"],
        certifications=["AWS Certified Solutions Architect (Preferred)"],
        responsibilities=[
            "Design and build scalable REST APIs in FastAPI and Python",
            "Optimize PostgreSQL database queries and migrations",
            "Deploy containerized microservices to cloud environments"
        ],
        requirements=[
            JobRequirement(
                requirement_id="REQ_ENG_01",
                description="3+ years experience building REST APIs with Python and FastAPI",
                skill="FastAPI",
                category="competency",
                importance="must_have",
                mandatory=True,
                weight=35.0,
                minimum_duration_months=36
            ),
            JobRequirement(
                requirement_id="REQ_ENG_02",
                description="Strong proficiency in PostgreSQL database design and query optimization",
                skill="PostgreSQL",
                category="competency",
                importance="must_have",
                mandatory=True,
                weight=25.0
            ),
            JobRequirement(
                requirement_id="REQ_ENG_03",
                description="Experience with Docker containerization and cloud deployment (AWS/GCP)",
                skill="Docker",
                category="competency",
                importance="preferred",
                mandatory=False,
                weight=15.0
            ),
            JobRequirement(
                requirement_id="REQ_ENG_04",
                description="Bachelor's degree in Computer Science or Software Engineering",
                skill="Computer Science",
                category="qualification",
                importance="must_have",
                mandatory=False,
                weight=10.0
            )
        ]
    )

    # Job 2: Cybersecurity & Information Security Domain
    job2 = JobProfile(
        job_id="JOB_CYBERSEC_01",
        title="Cybersecurity Analyst & Penetration Tester",
        description="Conduct vulnerability assessment, penetration testing, and security auditing across corporate network infrastructure and web applications.",
        domain=["Cybersecurity & Information Security"],
        min_experience_months=24,
        must_have_skills=["Vulnerability Assessment", "Penetration Testing", "Ethical Hacking", "CEH"],
        preferred_skills=["Wireshark", "Metasploit", "Burp Suite", "Linux", "Network Security"],
        education_requirements=["Degree in Cybersecurity, Computer Science, or Information Technology"],
        certifications=["Certified Ethical Hacker (CEH)", "CISSP (Preferred)"],
        responsibilities=[
            "Perform vulnerability scans and ethical hacking penetration tests",
            "Utilize Wireshark, Metasploit, and Nmap to identify security flaws",
            "Prepare detailed remediation reports for security vulnerabilities"
        ],
        requirements=[
            JobRequirement(
                requirement_id="REQ_SEC_01",
                description="Hands-on experience in Vulnerability Assessment & Penetration Testing",
                skill="Vulnerability Assessment",
                category="competency",
                importance="must_have",
                mandatory=True,
                weight=35.0,
                minimum_duration_months=24
            ),
            JobRequirement(
                requirement_id="REQ_SEC_02",
                description="Certified Ethical Hacker (CEH) or equivalent security certification",
                skill="CEH",
                category="certification",
                importance="must_have",
                mandatory=True,
                weight=30.0
            ),
            JobRequirement(
                requirement_id="REQ_SEC_03",
                description="Proficiency with security tools: Wireshark, Metasploit, Nmap, Burp Suite, and Linux",
                skill="Metasploit",
                category="competency",
                importance="preferred",
                mandatory=False,
                weight=20.0
            )
        ]
    )

    # Job 3: Finance & Accounting Domain
    job3 = JobProfile(
        job_id="JOB_FINANCE_01",
        title="Senior Financial Accountant",
        description="Manage monthly financial close operations, general ledger accounting, financial auditing, tax filings, and corporate financial statements.",
        domain=["Finance & Accounting"],
        min_experience_months=36,
        must_have_skills=["General Ledger", "Bookkeeping", "Financial Close", "Auditing"],
        preferred_skills=["Taxation", "Payroll", "Financial Analysis", "CPA"],
        education_requirements=["Bachelor's degree in Accounting, Finance, or Business Administration"],
        certifications=["CPA (Certified Public Accountant) or ACCA"],
        responsibilities=[
            "Oversee general ledger entries, trial balance, and month-end close procedures",
            "Prepare balance sheet reconciliations and income tax filings",
            "Coordinate internal and external financial audits"
        ],
        requirements=[
            JobRequirement(
                requirement_id="REQ_FIN_01",
                description="3+ years experience in General Ledger accounting and monthly financial close",
                skill="General Ledger",
                category="competency",
                importance="must_have",
                mandatory=True,
                weight=35.0,
                minimum_duration_months=36
            ),
            JobRequirement(
                requirement_id="REQ_FIN_02",
                description="Proven experience performing financial auditing and tax reporting",
                skill="Auditing",
                category="competency",
                importance="must_have",
                mandatory=True,
                weight=30.0
            ),
            JobRequirement(
                requirement_id="REQ_FIN_03",
                description="Bachelor's degree in Accounting, Finance, or Commerce (B.Com/MBA)",
                skill="Accounting",
                category="qualification",
                importance="must_have",
                mandatory=False,
                weight=15.0
            )
        ]
    )

    try:
        job_repo.save_job(job1)
        job_repo.save_job(job2)
        job_repo.save_job(job3)
        print("Successfully seeded 3 distinct domain job descriptions into database:")
        print(" 1. JOB_ENGINEERING_01: Senior FastAPI Backend Developer (Engineering & IT)")
        print(" 2. JOB_CYBERSEC_01: Cybersecurity Analyst & Penetration Tester (Cybersecurity & Security)")
        print(" 3. JOB_FINANCE_01: Senior Financial Accountant (Finance & Accounting)")
    except Exception as e:
        print(f"Error seeding jobs: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_jobs()

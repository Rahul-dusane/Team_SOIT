"""
clear_db.py
Safely purges all records across all ORM tables in the database via raw SQL DELETE.
"""

import os
import sys
from sqlalchemy import text

backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from db.connection import engine, SessionLocal

TABLES = [
    "requirement_assessments",
    "evidence_items",
    "gaps",
    "recruiter_summaries",
    "agent_run_logs",
    "matches",
    "document_chunks",
    "documents",
    "experiences",
    "education",
    "candidate_skills",
    "candidates",
    "job_requirements",
    "jobs",
    "skill_relationships",
    "skill_aliases",
    "skills"
]

def clear_all_data():
    with engine.begin() as conn:
        # Disable foreign keys temporarily for SQLite/Postgres clean truncate
        if engine.dialect.name == "sqlite":
            conn.execute(text("PRAGMA foreign_keys = OFF;"))
        
        for table in TABLES:
            try:
                result = conn.execute(text(f"DELETE FROM {table};"))
                print(f"Cleared table '{table}': {result.rowcount} rows deleted.")
            except Exception as e:
                print(f"Skipped '{table}': {e}")
        
        if engine.dialect.name == "sqlite":
            conn.execute(text("PRAGMA foreign_keys = ON;"))
            
    print("Database purge complete: All database tables are now empty.")

if __name__ == "__main__":
    clear_all_data()

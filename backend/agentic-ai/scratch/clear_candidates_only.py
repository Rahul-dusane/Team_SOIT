"""
clear_candidates_only.py
Purges all candidate records, documents, chunks, and matches from the database while keeping job descriptions intact.
"""

import os
import sys
from sqlalchemy import text

backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from db.connection import engine

CANDIDATE_TABLES = [
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
    "candidates"
]

def clear_candidate_data():
    with engine.begin() as conn:
        if engine.dialect.name == "sqlite":
            conn.execute(text("PRAGMA foreign_keys = OFF;"))
        
        for table in CANDIDATE_TABLES:
            try:
                result = conn.execute(text(f"DELETE FROM {table};"))
                print(f"Cleared table '{table}': {result.rowcount} rows deleted.")
            except Exception as e:
                print(f"Skipped '{table}': {e}")
        
        if engine.dialect.name == "sqlite":
            conn.execute(text("PRAGMA foreign_keys = ON;"))
            
    print("Candidate & match data purge complete. Job data preserved.")

if __name__ == "__main__":
    clear_candidate_data()

"""
connection.py
SQLAlchemy Database connection management supporting PostgreSQL/Supabase and SQLite fallback.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

def get_database_url() -> str:
    db_url = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL")
    if not db_url:
        # Fallback to local SQLite file for offline unit testing
        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "hirelens_local.db"))
        return f"sqlite:///{db_path}"
    
    # Fix potential postgres:// vs postgresql:// scheme issue
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    return db_url

DATABASE_URL = get_database_url()
IS_SQLITE = DATABASE_URL.startswith("sqlite")

connect_args = {"check_same_thread": False} if IS_SQLITE else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from db.models import Base as ModelsBase
    ModelsBase.metadata.create_all(bind=engine)

# Ensure tables exist on database initialization
try:
    init_db()
except Exception as e:
    print(f"[Warning] Failed to initialize DB tables automatically: {e}")

"""
connection.py
SQLAlchemy Database connection management supporting PostgreSQL/Supabase and SQLite fallback.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

Base = declarative_base()

from urllib.parse import quote_plus

def sanitize_database_url(url: str) -> str:
    """Encodes special characters in database passwords (e.g. '$' -> '%24') to prevent connection URI host parsing errors."""
    if not url or "[YOUR-PASSWORD]" in url:
        return url
    
    try:
        scheme_idx = url.find("://")
        if scheme_idx != -1:
            rest = url[scheme_idx + 3:]
            if "@" in rest:
                user_pass, host_db = rest.rsplit("@", 1)
                if ":" in user_pass:
                    user, raw_pass = user_pass.split(":", 1)
                    # Unquote first to prevent double-encoding if already quoted
                    from urllib.parse import unquote
                    unquoted_pass = unquote(raw_pass)
                    safe_pass = quote_plus(unquoted_pass)
                    return f"postgresql+psycopg://{user}:{safe_pass}@{host_db}"
    except Exception:
        pass
    
    if (url.startswith("postgres://") or url.startswith("postgresql://")) and not url.startswith("postgresql+"):
        url = url.replace("postgres://", "postgresql+psycopg://", 1).replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def get_database_url() -> str:
    # If TESTING env var is set, use local SQLite for fast isolated test execution
    if os.getenv("TESTING") == "true":
        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "hirelens_local.db"))
        return f"sqlite:///{db_path}"

    db_url = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL")
    if not db_url or "[YOUR-PASSWORD]" in db_url:
        # Fallback to local SQLite file for offline unit testing when placeholder password is present
        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "hirelens_local.db"))
        return f"sqlite:///{db_path}"
    
    return sanitize_database_url(db_url)

DATABASE_URL = get_database_url()
IS_SQLITE = DATABASE_URL.startswith("sqlite")

connect_args = {"check_same_thread": False} if IS_SQLITE else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from sqlalchemy import text

def check_db_health(db=None) -> dict:
    """Verifies live database connectivity by executing a probe query."""
    close_after = False
    if db is None:
        db = SessionLocal()
        close_after = True
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "connected",
            "dialect": engine.dialect.name,
            "is_sqlite": IS_SQLITE
        }
    except Exception as e:
        return {
            "status": "disconnected",
            "error": str(e),
            "is_sqlite": IS_SQLITE
        }
    finally:
        if close_after:
            db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initializes database tables after ORM models are registered."""
    from db.models import Base as ModelsBase
    ModelsBase.metadata.create_all(bind=engine)


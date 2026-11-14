"""
Database connection setup.
Uses SQLAlchemy so it works with Postgres (Supabase/Railway) with minimal changes.

For a quick start WITHOUT setting up Postgres yet, this defaults to a local
SQLite file (saferoute.db) so you can run everything immediately.
Switch DATABASE_URL in your .env to a real Postgres URL when ready --
no code changes needed elsewhere.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

# Falls back to local SQLite if no DATABASE_URL is set -- lets you start coding
# today without waiting to set up Supabase/Railway.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./saferoute.db")
# Render/Heroku-style Postgres URLs start with postgres:// which SQLAlchemy 2 rejects.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency -- yields a DB session per request, closes it after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

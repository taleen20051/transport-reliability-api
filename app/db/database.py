# Database engine and session factory used across the application

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Create the SQLAlchemy engine using the configured database URL
engine = create_engine(
    settings.DATABASE_URL,
    # Check connections before use to avoid stale connection errors
    pool_pre_ping=True,
)

# Create a reusable session factory for request-scoped database sessions
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)
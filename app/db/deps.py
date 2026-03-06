from __future__ import annotations

from collections.abc import Generator
from sqlalchemy.orm import Session

from app.db.database import SessionLocal

# Yield a database session for the duration of the request, then close it
def get_db() -> Generator[Session, None, None]:
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
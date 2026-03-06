from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing configuration using Argon2
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Hash a plain-text password before storing it.
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Compare a plain-text password with its stored hash.
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Build and sign a JWT access token with an expiry timestamp.
def create_access_token(subject: str | int, expires_minutes: int | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    # JWT payload contains the subject identifier and expiration time.
    to_encode: dict[str, Any] = {"sub": str(subject), "exp": expire}
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.deps import get_db
from app.models.user import User

# Extract bearer tokens from incoming authenticated requests
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Decode the JWT, extract the user id, and load the matching user record
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not identify credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode and validate the token using the configured secret and algorithm
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        sub = payload.get("sub")
        if sub is None:
            raise credentials_exception
        user_id = int(sub)
    except (JWTError, ValueError):
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise credentials_exception
    return user
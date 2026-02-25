from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.db.deps import get_db
from app.models.user import User
from app.schemas.auth import TokenOut, UserRegister

router = APIRouter(prefix="/auth", tags=["auth"])

AUTH_ERROR_RESPONSES = {
    400: {"description": "Bad Request (email already registered)"},
    401: {"description": "Unauthorized (invalid credentials)"},
    422: {"description": "Validation Error (invalid payload)"},
}


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    responses={400: AUTH_ERROR_RESPONSES[400], 422: AUTH_ERROR_RESPONSES[422]},
)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=payload.email, hashed_password=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"id": user.id, "email": user.email}


@router.post(
    "/login",
    response_model=TokenOut,
    responses={401: AUTH_ERROR_RESPONSES[401], 422: AUTH_ERROR_RESPONSES[422]},
)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(subject=user.id)

    # If your TokenOut schema has token_type, set it; if not, this still works if token_type is optional.
    return TokenOut(access_token=token, token_type="bearer")
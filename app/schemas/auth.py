# Pydantic schemas used for user registration and authentication responses

from pydantic import BaseModel, EmailStr, Field

# Request model for registering a new user account
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

# Response model returned after a successful login
class TokenOut(BaseModel):
    access_token: str

    # Token type used in the Authorization header for protected requests
    token_type: str = "bearer"
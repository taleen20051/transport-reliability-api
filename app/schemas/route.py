# Pydantic schemas for transport route request and response data

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

# Request model for creating a new route
class RouteCreate(BaseModel):

    # Route names must be non-empty and constrained to a sensible length
    name: str = Field(min_length=1, max_length=120)

    # Optional transport mode such as bus, train, or metro
    mode: Optional[str] = Field(default=None, max_length=50)

    # Optional operating company or service provider
    operator: Optional[str] = Field(default=None, max_length=120)


# Request model for partially updating route details
class RouteUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    mode: Optional[str] = Field(default=None, max_length=50)
    operator: Optional[str] = Field(default=None, max_length=120)


# Response model returned when route records are read from the API
class RouteOut(BaseModel):
    id: int
    name: str
    mode: Optional[str]
    operator: Optional[str]

    # Enable conversion from SQLAlchemy ORM objects to API response models
    model_config = ConfigDict(from_attributes=True)
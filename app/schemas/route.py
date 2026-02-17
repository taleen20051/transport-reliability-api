from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class RouteCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    mode: Optional[str] = Field(default=None, max_length=50)
    operator: Optional[str] = Field(default=None, max_length=120)


class RouteUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    mode: Optional[str] = Field(default=None, max_length=50)
    operator: Optional[str] = Field(default=None, max_length=120)


class RouteOut(BaseModel):
    id: int
    name: str
    mode: Optional[str]
    operator: Optional[str]

    class Config:
        from_attributes = True
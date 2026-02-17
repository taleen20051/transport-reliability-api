from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class StationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=180)
    lat: Optional[float] = None
    lon: Optional[float] = None


class StationUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=180)
    lat: Optional[float] = None
    lon: Optional[float] = None


class StationOut(BaseModel):
    id: int
    name: str
    lat: Optional[float]
    lon: Optional[float]

    class Config:
        from_attributes = True
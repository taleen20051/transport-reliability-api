# Pydantic schemas for station request and response data

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# Request model for creating a new station
class StationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=180)
    lat: Optional[float] = None
    lon: Optional[float] = None


# Request model for partially updating station details
class StationUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=180)
    lat: Optional[float] = None
    lon: Optional[float] = None


# Response model returned when station records are read from the API
class StationOut(BaseModel):
    id: int
    name: str
    lat: Optional[float]
    lon: Optional[float]

    # Allow response objects to be created directly from ORM model instances
    model_config = ConfigDict(from_attributes=True)
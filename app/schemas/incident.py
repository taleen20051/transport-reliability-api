# Pydantic schemas for creating, updating, and returning user incident data

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# Request model for submitting a new user-reported incident
class IncidentCreate(BaseModel):
    route_id: int
    
    # Station is optional because some incidents may affect a route generally rather than a specific stop
    station_id: Optional[int] = None

    # Delay must be non-negative
    delay_minutes: int = Field(ge=0)
    category: str
    description: str


# Request model for partial updates to an existing incident
class IncidentUpdate(BaseModel):
    delay_minutes: Optional[int] = Field(default=None, ge=0)
    category: Optional[str] = None
    description: Optional[str] = None


# Response model returned when incident records are read from the API
class IncidentOut(BaseModel):
    id: int
    user_id: int
    route_id: int
    station_id: Optional[int]
    reported_at: datetime
    delay_minutes: int
    category: str
    description: str

    # Allow Pydantic to build this schema directly from SQLAlchemy model instances
    model_config = ConfigDict(from_attributes=True)
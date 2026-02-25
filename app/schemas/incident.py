from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class IncidentCreate(BaseModel):
    route_id: int
    station_id: Optional[int] = None
    delay_minutes: int = Field(ge=0)
    category: str
    description: str


class IncidentUpdate(BaseModel):
    delay_minutes: Optional[int] = Field(default=None, ge=0)
    category: Optional[str] = None
    description: Optional[str] = None


class IncidentOut(BaseModel):
    id: int
    user_id: int
    route_id: int
    station_id: Optional[int]
    reported_at: datetime
    delay_minutes: int
    category: str
    description: str

    # Pydantic v2 replacement for class Config/from_attributes
    model_config = ConfigDict(from_attributes=True)
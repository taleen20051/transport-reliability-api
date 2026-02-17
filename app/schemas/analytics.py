from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class ReliabilityOut(BaseModel):
    route_id: int
    from_date: Optional[date]
    to_date: Optional[date]
    threshold_minutes: int
    total_incidents: int
    on_time_incidents: int
    reliability_percent: float


class DelayBucketOut(BaseModel):
    bucket: int  # hour (0-23) OR weekday (0-6)
    count: int
    avg_delay: float


class HotspotOut(BaseModel):
    station_id: int
    station_name: str
    incident_count: int
    avg_delay: float
    pain_index: float


class HotspotsResponse(BaseModel):
    window_days: int
    results: list[HotspotOut]
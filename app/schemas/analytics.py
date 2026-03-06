# Pydantic response schemas for analytics endpoints

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel

# Response model for route reliability calculations
class ReliabilityOut(BaseModel):
    route_id: int
    from_date: Optional[date]
    to_date: Optional[date]
    threshold_minutes: int
    total_incidents: int
    on_time_incidents: int
    reliability_percent: float

# Response model for grouped delay statistics by hour or weekday
class DelayBucketOut(BaseModel):

    # Bucket value represents either an hour (0-23) or a weekday (0-6)
    bucket: int
    count: int
    avg_delay: float

# Response model representing a single disruption hotspot station
class HotspotOut(BaseModel):
    station_id: int
    station_name: str
    incident_count: int
    avg_delay: float
    pain_index: float

# Wrapper response containing hotspot results for a given lookback window
class HotspotsResponse(BaseModel):
    window_days: int
    results: list[HotspotOut]
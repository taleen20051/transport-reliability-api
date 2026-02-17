from __future__ import annotations

from datetime import date, datetime, time, timezone, timedelta
from typing import Optional, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, Integer

from app.db.deps import get_db
from app.models.user_incident import UserIncident
from app.models.station import Station
from app.schemas.analytics import (
    ReliabilityOut,
    DelayBucketOut,
    HotspotOut,
    HotspotsResponse,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _date_to_utc_bounds(d: date) -> tuple[datetime, datetime]:
    """
    Convert a date into [start_of_day_utc, start_of_next_day_utc)
    so filtering is consistent and timezone-safe.
    """
    start = datetime.combine(d, time.min).replace(tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    return start, end


@router.get("/routes/{route_id}/reliability", response_model=ReliabilityOut)
def reliability_per_route(
    route_id: int,
    from_date: Optional[date] = Query(default=None, description="Filter incidents from this date (inclusive)"),
    to_date: Optional[date] = Query(default=None, description="Filter incidents to this date (inclusive)"),
    threshold_minutes: int = Query(default=5, ge=0, description="Delay threshold for 'on-time'"),
    db: Session = Depends(get_db),
):
    q = db.query(UserIncident).filter(UserIncident.route_id == route_id)

    if from_date:
        start, _ = _date_to_utc_bounds(from_date)
        q = q.filter(UserIncident.reported_at >= start)

    if to_date:
        _, end_exclusive = _date_to_utc_bounds(to_date)
        q = q.filter(UserIncident.reported_at < end_exclusive)

    total = q.count()
    if total == 0:
        return ReliabilityOut(
            route_id=route_id,
            from_date=from_date,
            to_date=to_date,
            threshold_minutes=threshold_minutes,
            total_incidents=0,
            on_time_incidents=0,
            reliability_percent=0.0,
        )

    on_time = q.filter(UserIncident.delay_minutes <= threshold_minutes).count()
    reliability_percent = round((on_time / total) * 100.0, 2)

    return ReliabilityOut(
        route_id=route_id,
        from_date=from_date,
        to_date=to_date,
        threshold_minutes=threshold_minutes,
        total_incidents=total,
        on_time_incidents=on_time,
        reliability_percent=reliability_percent,
    )


@router.get("/delays/distribution", response_model=list[DelayBucketOut])
def delay_distribution(
    group_by: str = "hour",
    route_id: int | None = None,
    db: Session = Depends(get_db),
):
    # Build the bucket expression (the thing we group by)
    if group_by == "hour":
        bucket_expr = func.extract("hour", UserIncident.reported_at).cast(Integer)
    elif group_by == "weekday":
        # 0-6 (Sun-Sat) in Postgres when using extract(dow)
        bucket_expr = func.extract("dow", UserIncident.reported_at).cast(Integer)
    else:
        raise HTTPException(status_code=400, detail="group_by must be 'hour' or 'weekday'")

    q = (
        db.query(
            bucket_expr.label("bucket"),
            func.count(UserIncident.id).label("count"),
            func.avg(UserIncident.delay_minutes).label("avg_delay"),
        )
        .select_from(UserIncident)
    )

    if route_id is not None:
        q = q.filter(UserIncident.route_id == route_id)

    # IMPORTANT: group_by/order_by using the *expression*, NOT "bucket" string
    rows = q.group_by(bucket_expr).order_by(bucket_expr).all()

    return [
        DelayBucketOut(bucket=int(bucket), count=int(count), avg_delay=float(avg_delay or 0.0))
        for (bucket, count, avg_delay) in rows
    ]


@router.get("/stations/hotspots", response_model=HotspotsResponse)
def hotspot_stations(
    window_days: int = Query(default=30, ge=1, le=365),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    since = datetime.now(timezone.utc) - timedelta(days=window_days)

    # Only incidents that have a station_id
    rows = (
        db.query(
            UserIncident.station_id.label("station_id"),
            func.count(UserIncident.id).label("incident_count"),
            func.avg(UserIncident.delay_minutes).label("avg_delay"),
        )
        .filter(UserIncident.station_id.isnot(None))
        .filter(UserIncident.reported_at >= since)
        .group_by(UserIncident.station_id)
        .all()
    )

    # Join station names + compute pain index = count * avg_delay
    results: list[HotspotOut] = []
    for r in rows:
        station = db.query(Station).filter(Station.id == r.station_id).first()
        station_name = station.name if station else f"station_{r.station_id}"

        avg_delay = float(r.avg_delay or 0.0)
        incident_count = int(r.incident_count)
        pain_index = round(incident_count * avg_delay, 2)

        results.append(
            HotspotOut(
                station_id=int(r.station_id),
                station_name=station_name,
                incident_count=incident_count,
                avg_delay=round(avg_delay, 2),
                pain_index=pain_index,
            )
        )

    results.sort(key=lambda x: x.pain_index, reverse=True)
    results = results[:limit]

    return HotspotsResponse(window_days=window_days, results=results)
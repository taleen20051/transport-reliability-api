# Router exposing analytical endpoints for transport reliability and delay patterns

from __future__ import annotations

from datetime import date, datetime, time, timezone, timedelta
from typing import Optional, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import Integer, func
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models.station import Station
from app.models.user_incident import UserIncident
from app.schemas.analytics import (
    DelayBucketOut,
    HotspotOut,
    HotspotsResponse,
    ReliabilityOut,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


# Reusable OpenAPI response descriptions for analytics endpoints
ANALYTICS_ERROR_RESPONSES = {
    400: {"description": "Bad Request (invalid query parameter)"},
    404: {"description": "Not Found (route/station not found where applicable)"},
    422: {"description": "Validation Error (invalid parameter type/range)"},
}


# Convert a calendar date into UTC start/end bounds for consistent date filtering
def _date_to_utc_bounds(d: date) -> tuple[datetime, datetime]:
    start = datetime.combine(d, time.min).replace(tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    return start, end


@router.get(
    "/routes/{route_id}/reliability",
    response_model=ReliabilityOut,
    responses={422: ANALYTICS_ERROR_RESPONSES[422]},
)


# Compute a simple reliability score based on the proportion of incidents
# whose delay is less than or equal to a configurable threshold
def reliability_per_route(
    route_id: int,
    from_date: Optional[date] = Query(
        default=None, description="Filter incidents from this date (inclusive)"
    ),
    to_date: Optional[date] = Query(
        default=None, description="Filter incidents to this date (inclusive)"
    ),
    threshold_minutes: int = Query(
        default=5, ge=0, description="Delay threshold for 'on-time' (minutes)"
    ),
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


@router.get(
    "/delays/distribution",
    response_model=list[DelayBucketOut],
    responses={400: ANALYTICS_ERROR_RESPONSES[400], 422: ANALYTICS_ERROR_RESPONSES[422]},
)

# Group incidents by hour or weekday to reveal temporal delay patterns
def delay_distribution(
    group_by: Literal["hour", "weekday"] = Query(
        default="hour", description="Bucket incidents by hour or weekday"
    ),
    route_id: int | None = Query(default=None, description="Optional route filter"),
    db: Session = Depends(get_db),
):
    # Build the bucket expression (grouping key)
    if group_by == "hour":
        bucket_expr = func.extract("hour", UserIncident.reported_at).cast(Integer)
    else:
        # 0-6 (Sun-Sat) in Postgres with extract(dow)
        bucket_expr = func.extract("dow", UserIncident.reported_at).cast(Integer)

    q = db.query(
        bucket_expr.label("bucket"),
        func.count(UserIncident.id).label("count"),
        func.avg(UserIncident.delay_minutes).label("avg_delay"),
    ).select_from(UserIncident)

    if route_id is not None:
        q = q.filter(UserIncident.route_id == route_id)

    # Aggregate the grouped results and return them in bucket order
    rows = q.group_by(bucket_expr).order_by(bucket_expr).all()

    return [
        DelayBucketOut(
            bucket=int(bucket),
            count=int(count),
            avg_delay=float(avg_delay or 0.0),
        )
        for (bucket, count, avg_delay) in rows
    ]


@router.get(
    "/stations/hotspots",
    response_model=HotspotsResponse,
    responses={422: ANALYTICS_ERROR_RESPONSES[422]},
)

# Rank stations by disruption severity using incident frequency and average delay
def hotspot_stations(
    window_days: int = Query(default=30, ge=1, le=365, description="Lookback window in days"),
    limit: int = Query(default=10, ge=1, le=50, description="Max results to return"),
    db: Session = Depends(get_db),
):
    since = datetime.now(timezone.utc) - timedelta(days=window_days)

    # Aggregate incident counts and average delays per station in a single query
    rows = (
        db.query(
            UserIncident.station_id.label("station_id"),
            Station.name.label("station_name"),
            func.count(UserIncident.id).label("incident_count"),
            func.avg(UserIncident.delay_minutes).label("avg_delay"),
        )
        .join(Station, Station.id == UserIncident.station_id)
        .filter(UserIncident.station_id.isnot(None))
        .filter(UserIncident.reported_at >= since)
        .group_by(UserIncident.station_id, Station.name)
        .all()
    )

    results: list[HotspotOut] = []
    for station_id, station_name, incident_count, avg_delay in rows:
        avg_delay_f = float(avg_delay or 0.0)
        incident_count_i = int(incident_count)

        # Pain Index combines how often disruptions occur with how severe they are
        pain_index = round(incident_count_i * avg_delay_f, 2)

        results.append(
            HotspotOut(
                station_id=int(station_id),
                station_name=station_name,
                incident_count=incident_count_i,
                avg_delay=round(avg_delay_f, 2),
                pain_index=pain_index,
            )
        )

    # Sort stations by highest disruption score first, then apply the result limit.
    results.sort(key=lambda x: x.pain_index, reverse=True)
    results = results[:limit]

    return HotspotsResponse(window_days=window_days, results=results)
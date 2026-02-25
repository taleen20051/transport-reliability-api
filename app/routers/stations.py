from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.auth_deps import get_current_user
from app.db.deps import get_db
from app.models.station import Station
from app.models.user import User
from app.schemas.station import StationCreate, StationOut, StationUpdate

router = APIRouter(prefix="/stations", tags=["stations"])

STATION_ERROR_RESPONSES = {
    401: {"description": "Unauthorized (missing/invalid Bearer token)"},
    404: {"description": "Not Found (station_id does not exist)"},
    422: {"description": "Validation Error (invalid payload)"},
}


@router.post(
    "",
    response_model=StationOut,
    status_code=status.HTTP_201_CREATED,
    responses={401: STATION_ERROR_RESPONSES[401], 422: STATION_ERROR_RESPONSES[422]},
)
def create_station(
    payload: StationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # protect write
):
    station = Station(**payload.model_dump())
    db.add(station)
    db.commit()
    db.refresh(station)
    return station


@router.get(
    "/{station_id}",
    response_model=StationOut,
    responses={404: STATION_ERROR_RESPONSES[404]},
)
def get_station(station_id: int, db: Session = Depends(get_db)):
    station = db.query(Station).filter(Station.id == station_id).first()
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    return station


@router.get("", response_model=list[StationOut])
def list_stations(
    db: Session = Depends(get_db),
    limit: int = Query(default=100, ge=1, le=500, description="Max number of stations to return"),
    offset: int = Query(default=0, ge=0, description="Pagination offset"),
):
    return db.query(Station).order_by(Station.id).offset(offset).limit(limit).all()


@router.patch(
    "/{station_id}",
    response_model=StationOut,
    responses=STATION_ERROR_RESPONSES,
)
def update_station(
    station_id: int,
    payload: StationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # protect write
):
    station = db.query(Station).filter(Station.id == station_id).first()
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(station, key, value)

    db.commit()
    db.refresh(station)
    return station


@router.delete(
    "/{station_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={401: STATION_ERROR_RESPONSES[401], 404: STATION_ERROR_RESPONSES[404]},
)
def delete_station(
    station_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # protect write
):
    station = db.query(Station).filter(Station.id == station_id).first()
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    db.delete(station)
    db.commit()
    return None
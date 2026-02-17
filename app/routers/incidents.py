from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models.user_incident import UserIncident
from app.schemas.incident import (
    IncidentCreate,
    IncidentUpdate,
    IncidentOut,
)

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.post(
    "",
    response_model=IncidentOut,
    status_code=status.HTTP_201_CREATED,
)
def create_incident(payload: IncidentCreate, db: Session = Depends(get_db)):
    incident = UserIncident(**payload.dict())

    db.add(incident)
    db.commit()
    db.refresh(incident)

    return incident


@router.get("/{incident_id}", response_model=IncidentOut)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = (
        db.query(UserIncident)
        .filter(UserIncident.id == incident_id)
        .first()
    )

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    return incident


@router.patch("/{incident_id}", response_model=IncidentOut)
def update_incident(
    incident_id: int,
    payload: IncidentUpdate,
    db: Session = Depends(get_db),
):
    incident = (
        db.query(UserIncident)
        .filter(UserIncident.id == incident_id)
        .first()
    )

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    for key, value in payload.dict(exclude_unset=True).items():
        setattr(incident, key, value)

    db.commit()
    db.refresh(incident)

    return incident


@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = (
        db.query(UserIncident)
        .filter(UserIncident.id == incident_id)
        .first()
    )

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    db.delete(incident)
    db.commit()
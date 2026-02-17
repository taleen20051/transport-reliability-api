from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.auth_deps import get_current_user
from app.models.user import User

from app.db.deps import get_db
from app.models.user_incident import UserIncident
from app.schemas.incident import (
    IncidentCreate,
    IncidentUpdate,
    IncidentOut,
)

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.post("", response_model=IncidentOut, status_code=status.HTTP_201_CREATED)
def create_incident(
    payload: IncidentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    incident = UserIncident(user_id=current_user.id, **payload.dict())
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
    current_user: User = Depends(get_current_user),
):
    incident = (
        db.query(UserIncident)
        .filter(UserIncident.id == incident_id)
        .first()
    )

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    # add this ownership check HERE (right after the 404 check)
    if incident.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    for key, value in payload.dict(exclude_unset=True).items():
        setattr(incident, key, value)

    db.commit()
    db.refresh(incident)

    return incident


@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    incident = (
        db.query(UserIncident)
        .filter(UserIncident.id == incident_id)
        .first()
    )

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    # add this ownership check HERE (right after the 404 check)
    if incident.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    db.delete(incident)
    db.commit()
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.auth_deps import get_current_user
from app.db.deps import get_db
from app.models.user import User
from app.models.user_incident import UserIncident
from app.schemas.incident import IncidentCreate, IncidentOut, IncidentUpdate

router = APIRouter(prefix="/incidents", tags=["incidents"])

INCIDENT_ERROR_RESPONSES = {
    401: {"description": "Unauthorized (missing/invalid Bearer token)"},
    403: {"description": "Forbidden (authenticated but not the owner of the incident)"},
    404: {"description": "Not Found (incident_id does not exist)"},
    422: {"description": "Validation Error (invalid payload)"},
}


@router.post(
    "",
    response_model=IncidentOut,
    status_code=status.HTTP_201_CREATED,
    responses={401: INCIDENT_ERROR_RESPONSES[401], 422: INCIDENT_ERROR_RESPONSES[422]},
)
def create_incident(
    payload: IncidentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Pydantic v2: use model_dump()
    incident = UserIncident(user_id=current_user.id, **payload.model_dump())
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


@router.get(
    "/{incident_id}",
    response_model=IncidentOut,
    responses={404: INCIDENT_ERROR_RESPONSES[404]},
)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(UserIncident).filter(UserIncident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.patch(
    "/{incident_id}",
    response_model=IncidentOut,
    responses=INCIDENT_ERROR_RESPONSES,
)
def update_incident(
    incident_id: int,
    payload: IncidentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    incident = db.query(UserIncident).filter(UserIncident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    # Ownership enforcement (403)
    if incident.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(incident, key, value)

    db.commit()
    db.refresh(incident)
    return incident


@router.delete(
    "/{incident_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=INCIDENT_ERROR_RESPONSES,
)
def delete_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    incident = db.query(UserIncident).filter(UserIncident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    # Ownership enforcement (403)
    if incident.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    db.delete(incident)
    db.commit()
    return None
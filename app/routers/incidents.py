# Router for creating, reading, updating, and deleting user-reported incidents

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.auth_deps import get_current_user
from app.db.deps import get_db
from app.models.route import Route
from app.models.station import Station
from app.models.user import User
from app.models.user_incident import UserIncident
from app.schemas.incident import IncidentCreate, IncidentOut, IncidentUpdate

router = APIRouter(prefix="/incidents", tags=["incidents"])

# Reusable OpenAPI response descriptions for incident endpoints
INCIDENT_ERROR_RESPONSES = {
    401: {"description": "Unauthorized (missing/invalid Bearer token)"},
    403: {"description": "Forbidden (authenticated but not the owner of the incident)"},
    404: {"description": "Not Found (incident, route, or station does not exist)"},
    422: {"description": "Validation Error (invalid payload)"},
}


@router.post(
    "",
    response_model=IncidentOut,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: INCIDENT_ERROR_RESPONSES[401],
        404: INCIDENT_ERROR_RESPONSES[404],
        422: INCIDENT_ERROR_RESPONSES[422],
    },
)

# Create a new incident linked to the currently authenticated user
def create_incident(
    payload: IncidentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Check that the referenced route exists before inserting
    route = db.query(Route).filter(Route.id == payload.route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    # Check that the referenced station exists before inserting
    if payload.station_id is not None:
        station = db.query(Station).filter(Station.id == payload.station_id).first()
        if not station:
            raise HTTPException(status_code=404, detail="Station not found")

    # Attach the incident to the logged-in user rather than trusting client input
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

# Retrieve a single incident by its identifier
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

# Update an existing incident, but only if it belongs to the authenticated user
def update_incident(
    incident_id: int,
    payload: IncidentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    incident = db.query(UserIncident).filter(UserIncident.id == incident_id).first()

    # Check that the incident exists before applying ownership rules
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    # Prevent users from editing incidents reported by someone else
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

# Delete an incident, restricted to the user who originally created it
def delete_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    incident = db.query(UserIncident).filter(UserIncident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if incident.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    # Remove the incident permanently once existence and ownership checks pass
    db.delete(incident)
    db.commit()
    return None
# Router exposing CRUD operations for transport routes

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.auth_deps import get_current_user
from app.db.deps import get_db
from app.models.route import Route
from app.models.user import User
from app.schemas.route import RouteCreate, RouteOut, RouteUpdate

router = APIRouter(prefix="/routes", tags=["routes"])

# Reusable OpenAPI response descriptions for route endpoints
ROUTE_ERROR_RESPONSES = {
    401: {"description": "Unauthorized (missing/invalid Bearer token)"},
    404: {"description": "Not Found (route_id does not exist)"},
    422: {"description": "Validation Error (invalid payload)"},
}


@router.post(
    "",
    response_model=RouteOut,
    status_code=status.HTTP_201_CREATED,
    responses={401: ROUTE_ERROR_RESPONSES[401], 422: ROUTE_ERROR_RESPONSES[422]},
)

# Create a new transport route. Write access requires authentication
def create_route(
    payload: RouteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Build the ORM route object from the validated request payload
    route = Route(**payload.model_dump())
    db.add(route)
    db.commit()
    db.refresh(route)
    return route


@router.get(
    "/{route_id}",
    response_model=RouteOut,
    responses={404: ROUTE_ERROR_RESPONSES[404]},
)

# Fetch a single route by its identifier
def get_route(route_id: int, db: Session = Depends(get_db)):
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route


@router.get("", response_model=list[RouteOut])
# Return a paginated list of routes for browsing or lookup
def list_routes(
    db: Session = Depends(get_db),
    limit: int = Query(default=100, ge=1, le=500, description="Max number of routes to return"),
    offset: int = Query(default=0, ge=0, description="Pagination offset"),
):
    # Apply a stable id ordering so pagination remains predictable
    return db.query(Route).order_by(Route.id).offset(offset).limit(limit).all()


@router.patch(
    "/{route_id}",
    response_model=RouteOut,
    responses=ROUTE_ERROR_RESPONSES,
)

# Update an existing route using only fields supplied in the request
def update_route(
    route_id: int,
    payload: RouteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Partial update: only overwrite fields explicitly provided by the client
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(route, key, value)

    db.commit()
    db.refresh(route)
    return route


@router.delete(
    "/{route_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={401: ROUTE_ERROR_RESPONSES[401], 404: ROUTE_ERROR_RESPONSES[404]},
)

# Delete a route after confirming it exists
def delete_route(
    route_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # protect write
):
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    db.delete(route)
    db.commit()
    return None
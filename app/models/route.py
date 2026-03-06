# SQLAlchemy model representing a public transport route

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.route_station import RouteStation
    from app.models.user_incident import UserIncident


# Represents a route in the transport system (for example, a bus line or train line)
class Route(Base):
    __tablename__ = "routes"

    # Unique identifier for the route
    id: Mapped[int] = mapped_column(primary_key=True)

    # Route name or code visible to users
    name: Mapped[str] = mapped_column(String(120), nullable=False)

    # Transport mode such as bus, train, or metro
    mode: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Company or organisation operating the route
    operator: Mapped[str | None] = mapped_column(String(120), nullable=True)

    # Incidents reported that affect this route
    incidents: Mapped[list["UserIncident"]] = relationship(back_populates="route")

    # Association objects linking this route to its stations
    stations_link: Mapped[list["RouteStation"]] = relationship(back_populates="route")
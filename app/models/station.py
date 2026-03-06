# SQLAlchemy model representing a transport station or stop

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.route_station import RouteStation
    from app.models.user_incident import UserIncident


# Represents a station within the transport network
class Station(Base):
    __tablename__ = "stations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False)

    # Latitude coordinate (optional)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Longitude coordinate (optional)
    lon: Mapped[float | None] = mapped_column(Float, nullable=True)

    incidents: Mapped[list["UserIncident"]] = relationship(
        back_populates="station",
        cascade="all, delete-orphan",
    )

    # Association objects linking the station to routes
    routes_link: Mapped[list["RouteStation"]] = relationship(
        back_populates="station",
        cascade="all, delete-orphan",
    )
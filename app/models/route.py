from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.route_station import RouteStation
    from app.models.user_incident import UserIncident


class Route(Base):
    __tablename__ = "routes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    mode: Mapped[str | None] = mapped_column(String(50), nullable=True)
    operator: Mapped[str | None] = mapped_column(String(120), nullable=True)

    incidents: Mapped[list["UserIncident"]] = relationship(back_populates="route")
    stations_link: Mapped[list["RouteStation"]] = relationship(back_populates="route")
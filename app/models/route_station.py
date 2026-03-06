from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.route import Route
    from app.models.station import Station


# Association table implementing the many-to-many relationship
# between routes and stations, with an additional stop order
class RouteStation(Base):
    __tablename__ = "route_stations"

    # Primary key for this association record
    id: Mapped[int] = mapped_column(primary_key=True)

    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id", ondelete="CASCADE"), nullable=False)
    station_id: Mapped[int] = mapped_column(ForeignKey("stations.id", ondelete="CASCADE"), nullable=False)

    # Indicates the order of the station within the route
    stop_sequence: Mapped[int] = mapped_column(nullable=False)

    # Prevent duplicate station assignments or duplicate stop order within the same route
    __table_args__ = (
        UniqueConstraint("route_id", "station_id", name="uq_route_station"),
        UniqueConstraint("route_id", "stop_sequence", name="uq_route_stop_sequence"),
    )
    # Relationship back to the Route and Station models
    route: Mapped["Route"] = relationship(back_populates="stations_link")
    station: Mapped["Station"] = relationship(back_populates="routes_link")
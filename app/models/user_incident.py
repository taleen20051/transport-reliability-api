# SQLAlchemy model representing a disruption reported by a user

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.route import Route
    from app.models.station import Station
    from app.models.user import User


# Stores a user-reported incident affecting the transport network
class UserIncident(Base):
    __tablename__ = "user_incidents"

    id: Mapped[int] = mapped_column(primary_key=True)

    # User who reported the incident
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Route affected by the disruption
    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id", ondelete="CASCADE"), nullable=False)
    station_id: Mapped[int | None] = mapped_column(ForeignKey("stations.id", ondelete="SET NULL"), nullable=True)

    # Timestamp of when the incident was reported
    reported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Delay duration in minutes caused by the incident
    delay_minutes: Mapped[int] = mapped_column(nullable=False)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="incidents")

    # Relationship back to the affected route
    route: Mapped["Route"] = relationship(back_populates="incidents")

    # Relationship back to the affected station
    station: Mapped["Station"] = relationship(back_populates="incidents")
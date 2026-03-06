# SQLAlchemy model representing an authenticated user of the API

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.user_incident import UserIncident


# Users can authenticate and report transport incidents
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Email used for login and identification
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)

    # Securely stored password hash (never plain text)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Incidents submitted by this user
    incidents: Mapped[list["UserIncident"]] = relationship(back_populates="user")
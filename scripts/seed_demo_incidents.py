from __future__ import annotations

import os
import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.user_incident import UserIncident
from app.models.route import Route
from app.models.station import Station

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set. Ensure your .env is loaded or export it in your shell.")


def main():
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)

    random.seed(42)

    with SessionLocal() as db:
        routes = db.query(Route).all()
        stations = db.query(Station).all()

        if not routes or not stations:
            raise RuntimeError("Create at least 1 route and 1 station first (via Swagger).")

        # pick an existing user_id (you have users 3 and 4 already)
        user_id = 3

        now = datetime.now(timezone.utc)
        new_incidents = []

        # create 60 incidents spread over last 14 days at varying hours/days
        for i in range(60):
            route = random.choice(routes)
            station = random.choice(stations)

            days_ago = random.randint(0, 13)
            hour = random.randint(6, 23)
            minute = random.randint(0, 59)

            reported_at = (now - timedelta(days=days_ago)).replace(
                hour=hour, minute=minute, second=0, microsecond=0
            )

            delay = random.choice([0, 2, 3, 5, 7, 10, 12, 15, 20, 30])
            category = random.choice(["delay", "cancellation", "crowding", "signal", "weather"])

            new_incidents.append(
                UserIncident(
                    user_id=user_id,
                    route_id=route.id,
                    station_id=station.id,
                    reported_at=reported_at,
                    delay_minutes=delay,
                    category=category,
                    description=f"Seeded incident {i+1}",
                )
            )

        db.add_all(new_incidents)
        db.commit()

        print(f" Seeded {len(new_incidents)} demo incidents.")


if __name__ == "__main__":
    main()
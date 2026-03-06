# Script used to generate synthetic incident data for testing analytics endpoints

from __future__ import annotations

import os
import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.user_incident import UserIncident
from app.models.route import Route
from app.models.station import Station


# Database connection string loaded from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set. Ensure your .env is loaded or export it in your shell.")


# Populate the database with randomly generated incident records
def main():
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)

    # Seed the random generator to make the demo data reproducible
    random.seed(42)

    with SessionLocal() as db:
        # Retrieve existing routes and stations to attach incidents to
        routes = db.query(Route).all()
        stations = db.query(Station).all()

        # Ensure the database already contains routes and stations
        if not routes or not stations:
            raise RuntimeError("Create at least 1 route and 1 station first (via Swagger).")

        # Use an existing user account to associate with generated incidents
        user_id = 3

        # Current timestamp used to generate incidents within the past two weeks
        now = datetime.now(timezone.utc)
        new_incidents = []

        # Generate a set of synthetic incidents with varied routes, stations, delays, and times
        for i in range(60):
            route = random.choice(routes)
            station = random.choice(stations)

            days_ago = random.randint(0, 13)
            hour = random.randint(6, 23)
            minute = random.randint(0, 59)

            # Spread incidents across different days and hours to support analytics testing
            reported_at = (now - timedelta(days=days_ago)).replace(
                hour=hour, minute=minute, second=0, microsecond=0
            )


            # Random delay values to simulate realistic disruption severity
            delay = random.choice([0, 2, 3, 5, 7, 10, 12, 15, 20, 30])
            category = random.choice(["delay", "cancellation", "crowding", "signal", "weather"])


            # Create a new ORM incident object and store it in the batch
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
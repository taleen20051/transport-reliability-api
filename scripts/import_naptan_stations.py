"""
Import a small sample of REAL UK public transport access nodes (NaPTAN) into the stations table.

Source (DfT NaPTAN CSV endpoint):
https://naptan.api.dft.gov.uk/v1/access-nodes?dataFormat=csv

Usage:
  PYTHONPATH=$(pwd) python scripts/import_naptan_stations.py --limit 50

Notes:
- This script intentionally imports a limited number of rows (default 50)
  to keep the coursework demo fast + reproducible.
- It avoids duplicates by checking for an existing station with same
  (name, lat, lon).
"""

from __future__ import annotations

import argparse
import csv
import io
import os
from typing import Optional

import requests
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.models.station import Station

NAPTAN_CSV_URL = "https://naptan.api.dft.gov.uk/v1/access-nodes?dataFormat=csv"


# Helper to safely read required environment variables
def _get_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}\n"
            f"Tip: export it or load your .env before running this script."
        )
    return value


# Convert string values to float while safely handling empty or invalid values
def _safe_float(s: Optional[str]) -> Optional[float]:
    if s is None:
        return None
    s = s.strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


# Main import routine that downloads the NaPTAN dataset and inserts a small sample into the database
def main(limit: int, timeout: int) -> None:
    database_url = _get_env("DATABASE_URL")

    # Download the NaPTAN CSV dataset from the official DfT endpoint
    resp = requests.get(NAPTAN_CSV_URL, timeout=timeout)
    resp.raise_for_status()

    # Parse the CSV so each row can be accessed as a dictionary
    csv_text = resp.text
    reader = csv.DictReader(io.StringIO(csv_text))

    # Create a SQLAlchemy connection to the project's database
    engine = create_engine(database_url, future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

    inserted = 0
    skipped = 0

    with SessionLocal() as db:

        # Iterate through dataset rows until the requested sample size is reached
        for row in reader:
            if inserted >= limit:
                break

            # Extract the station name and coordinates from the dataset row
            name = (row.get("CommonName") or "").strip()
            lat = _safe_float(row.get("Latitude"))
            lon = _safe_float(row.get("Longitude"))

            # Skip rows that do not contain usable station information
            if not name or lat is None or lon is None:
                skipped += 1
                continue

            # Prevent inserting duplicate stations with the same name and coordinates
            existing = db.execute(
                select(Station).where(
                    Station.name == name,
                    Station.lat == lat,
                    Station.lon == lon,
                )
            ).scalar_one_or_none()

            if existing:
                skipped += 1
                continue

            # Insert the new station record
            db.add(Station(name=name, lat=lat, lon=lon))
            inserted += 1

        # Persist all inserted stations to the database
        db.commit()

    print(f"NaPTAN import complete. Inserted={inserted}, Skipped={skipped}, Limit={limit}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import NaPTAN stations into the DB (sample).")
    parser.add_argument("--limit", type=int, default=50, help="Number of stations to import (default: 50)")
    parser.add_argument("--timeout", type=int, default=30, help="HTTP timeout seconds (default: 30)")
    args = parser.parse_args()

    if args.limit < 1 or args.limit > 5000:
        raise SystemExit("Please choose a sensible --limit (1..5000) for a coursework demo.")

    main(limit=args.limit, timeout=args.timeout)
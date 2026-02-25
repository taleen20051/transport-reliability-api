# **Transport Reliability & Incident Analytics API**

This project implements a RESTful API for analysing public transport reliability using route data, station data, and user-reported delay incidents. It provides secure CRUD operations and analytical endpoints for evaluating transport performance.

## **Project Overview**

The API models:

* Routes
* Stations
* User-reported incidents (delays/disruptions) created by authenticated users

It supports:

* CRUD operations for core entities
* JWT-secured write operations
* Analytics endpoints (reliability, delay distributions, hotspot stations)
* PostgreSQL persistence with SQLAlchemy + Alembic migrations
* OpenAPI / Swagger documentation

## **Tech Stack**

* FastAPI (Python)
* PostgreSQL
* SQLAlchemy
* Alembic
* Argon2 (password hashing)
* JWT (authentication)
* pytest (testing)
* Uvicorn (server)

## **Database Schema**

Core tables:

* users
* routes
* stations
* route_stations (junction table)
* user_incidents

Key rules:

* A user can create many incidents
* Users can only update/delete incidents they created (ownership enforcement)
* Routes and stations are linked via route_stations

## **Authentication**

JWT Bearer tokens.

Endpoints:

* POST /auth/register
* POST /auth/login

Protected endpoints (JWT required):

* POST /routes
* POST /stations
* POST /incidents
* PATCH /incidents/{id}
* DELETE /incidents/{id}

Ownership rule:

* Only the incident creator may PATCH/DELETE their incident

## **CRUD Endpoints**

Routes:

* POST /routes
* GET /routes
* GET /routes/{id}
* PATCH /routes/{id}
* DELETE /routes/{id}

Stations:

* POST /stations
* GET /stations
* GET /stations/{id}
* PATCH /stations/{id}
* DELETE /stations/{id}

Incidents:

* POST /incidents
* GET /incidents/{id}
* PATCH /incidents/{id}
* DELETE /incidents/{id}

## **Analytics Endpoints**

Delay distribution:

* GET /analytics/delays/distribution?group_by=hour
* GET /analytics/delays/distribution?group_by=weekday

Route reliability:

* GET /analytics/routes/{route_id}/reliability

Reliability definition:

* An incident is considered on-time if delay_minutes <= threshold_minutes (default 5)
* reliability_percent = (on_time_incidents / total_incidents) * 100

Hotspot stations:

* GET /analytics/stations/hotspots?window_days=30&limit=10

Hotspot ranking uses:

* pain_index = incident_count * avg_delay

## **Smoke Test (Manual API Verification)**

Assumes the API is running locally at:

http://127.0.0.1:8000

1. Register

curl -i -X POST “http://127.0.0.1:8000/auth/register”** **

-H “Content-Type: application/json”** **

-d ‘{“email”:“smoke@example.com”,“password”:“StrongPass123”}’

2. Login (copy token)

curl -s -X POST “http://127.0.0.1:8000/auth/login”** **

-H “Content-Type: application/x-www-form-urlencoded”** **

-d “username=smoke@example.com&password=StrongPass123”

Copy the access_token from the response and set it:

export TOKEN=“PASTE_TOKEN_HERE”

3. Create route (JWT required)

curl -s -X POST “http://127.0.0.1:8000/routes”** **

-H “Authorization: Bearer $TOKEN”** **

-H “Content-Type: application/json”** **

-d ‘{“name”:“Smoke Route”,“mode”:“bus”,“operator”:“Test”}’ | python -m json.tool

4. Create station (JWT required)

curl -s -X POST “http://127.0.0.1:8000/stations”** **

-H “Authorization: Bearer $TOKEN”** **

-H “Content-Type: application/json”** **

-d ‘{“name”:“Smoke Station”,“lat”:53.8,“lon”:-1.55}’ | python -m json.tool

5. Create incident (JWT required)

curl -s -X POST “http://127.0.0.1:8000/incidents”** **

-H “Authorization: Bearer $TOKEN”** **

-H “Content-Type: application/json”** **

-d ‘{“route_id”:5,“station_id”:3,“delay_minutes”:12,“category”:“delay”,“description”:“Smoke test incident”}’ | python -m json.tool

6. Run analytics (public)

curl -s “http://127.0.0.1:8000/analytics/delays/distribution?group_by=hour” | python -m json.tool

curl -s “http://127.0.0.1:8000/analytics/delays/distribution?group_by=weekday” | python -m json.tool

curl -s “http://127.0.0.1:8000/analytics/routes/5/reliability” | python -m json.tool

curl -s “http://127.0.0.1:8000/analytics/stations/hotspots?window_days=30&limit=10” | python -m json.tool

## **Running Locally**

1. Clone

git clone <repository_url>

cd transport-reliability-api

2. Virtual environment

python -m venv .venv

source .venv/bin/activate

3. Install dependencies

pip install -r requirements.txt

4. Environment variables

Create a .env file in the project root:

DATABASE_URL=postgresql+psycopg2://<db_user>:<db_password>@localhost:5432/transportdb

JWT_SECRET=<your_secret_here>

Optional (recommended for tests):

TEST_DATABASE_URL=postgresql+psycopg2://<db_user>:<db_password>@localhost:5432/transportdb_test

5. Run migrations

alembic upgrade head

6. Start server

uvicorn app.main:app –reload

## **API Documentation**

Swagger UI:

http://127.0.0.1:8000/docs

OpenAPI JSON:

http://127.0.0.1:8000/openapi.json

Exported PDF (in this repo):

docs/api-documentation.pdf

## **Demo Dataset (Seeding)**

Seed demo incidents:

export $(grep -v ‘^#’ .env | xargs)

PYTHONPATH=$(pwd) python scripts/seed_demo_incidents.py

## **Testing**

Run test suite:

export $(grep -v ‘^#’ .env | xargs)

pytest -q

## **Deployment**

Live deployment URL:

TO BE ADDED

After deployment:

* Replace base URL in this README
* Re-run the Smoke Test against the deployed base URL

## **Version Control**

This repository uses incremental Git commits to demonstrate development progress:

* database models and migrations
* CRUD endpoints
* authentication and ownership enforcement
* analytics endpoints
* seeding script
* tests and documentation

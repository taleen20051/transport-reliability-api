Base URLs

Local: http://127.0.0.1:8000

Deployed: REPLACE_WITH_DEPLOYED_BASE_URL

Authentication overview

This API uses JWT Bearer authentication.

Flow:

1. Register a user with POST /auth/register
2. Login with POST /auth/login to obtain an access_token
3. For protected endpoints, send the token in the header:

Authorization: Bearer <access_token>

Protected endpoints:

* POST /routes
* POST /stations
* POST /incidents
* PATCH /incidents/{id}
* DELETE /incidents/{id}

Analytics endpoints are public (no token required).

Example: Auth (Register and Login)

POST /auth/register

Request:

curl -i -X POST “http://127.0.0.1:8000/auth/register”** **

-H “Content-Type: application/json”** **

-d ‘{“email”:“smoke@example.com”,“password”:“StrongPass123”}’

Response (201):

{

“id”: 3,

“email”: “smoke@example.com”

}

POST /auth/login

Request:

curl -s -X POST “http://127.0.0.1:8000/auth/login”** **

-H “Content-Type: application/x-www-form-urlencoded”** **

-d “username=smoke@example.com&password=StrongPass123”

Response (200):

{

“access_token”: “PASTE_TOKEN_HERE”,

“token_type”: “bearer”

}

Example: Routes (CRUD)

POST /routes (protected)

Request:

curl -s -X POST “http://127.0.0.1:8000/routes”** **

-H “Authorization: Bearer PASTE_TOKEN_HERE”** **

-H “Content-Type: application/json”** **

-d ‘{“name”:“Smoke Route”,“mode”:“bus”,“operator”:“Test”}’

Response (201):

{

“id”: 5,

“name”: “Smoke Route”,

“mode”: “bus”,

“operator”: “Test”

}

GET /routes/{id}

Request:

curl -s “http://127.0.0.1:8000/routes/5”

Response (200):

{

“id”: 5,

“name”: “Smoke Route”,

“mode”: “bus”,

“operator”: “Test”

}

Example: Stations (CRUD)

POST /stations (protected)

Request:

curl -s -X POST “http://127.0.0.1:8000/stations”** **

-H “Authorization: Bearer PASTE_TOKEN_HERE”** **

-H “Content-Type: application/json”** **

-d ‘{“name”:“Smoke Station”,“lat”:53.8,“lon”:-1.55}’

Response (201):

{

“id”: 3,

“name”: “Smoke Station”,

“lat”: 53.8,

“lon”: -1.55

}

GET /stations/{id}

Request:

curl -s “http://127.0.0.1:8000/stations/3”

Response (200):

{

“id”: 3,

“name”: “Smoke Station”,

“lat”: 53.8,

“lon”: -1.55

}

Example: Incidents (CRUD + Ownership)

POST /incidents (protected)

Request:

curl -s -X POST “http://127.0.0.1:8000/incidents”** **

-H “Authorization: Bearer PASTE_TOKEN_HERE”** **

-H “Content-Type: application/json”** **

-d ‘{“route_id”:5,“station_id”:3,“delay_minutes”:12,“category”:“delay”,“description”:“Smoke test incident”}’

Response (201):

{

“id”: 67,

“user_id”: 3,

“route_id”: 5,

“station_id”: 3,

“reported_at”: “2026-02-17T22:06:26.412515Z”,

“delay_minutes”: 12,

“category”: “delay”,

“description”: “Smoke test incident”

}

GET /incidents/{id}

Request:

curl -s “http://127.0.0.1:8000/incidents/67”

Response (200):

{

“id”: 67,

“user_id”: 3,

“route_id”: 5,

“station_id”: 3,

“reported_at”: “2026-02-17T22:06:26.412515Z”,

“delay_minutes”: 12,

“category”: “delay”,

“description”: “Smoke test incident”

}

PATCH /incidents/{id} (protected, owner only)

Request:

curl -s -X PATCH “http://127.0.0.1:8000/incidents/67”** **

-H “Authorization: Bearer PASTE_TOKEN_HERE”** **

-H “Content-Type: application/json”** **

-d ‘{“delay_minutes”:20}’

Response (200):

{

“id”: 67,

“user_id”: 3,

“route_id”: 5,

“station_id”: 3,

“reported_at”: “2026-02-17T22:06:26.412515Z”,

“delay_minutes”: 20,

“category”: “delay”,

“description”: “Smoke test incident”

}

DELETE /incidents/{id} (protected, owner only)

Request:

curl -i -X DELETE “http://127.0.0.1:8000/incidents/67”** **

-H “Authorization: Bearer PASTE_TOKEN_HERE”

Response (204):

No Content

Example: Analytics

1. Delay distribution by hour

GET /analytics/delays/distribution?group_by=hour

Request:

curl -s “http://127.0.0.1:8000/analytics/delays/distribution?group_by=hour”

Response (200):

[

{“bucket”: 6, “count”: 4, “avg_delay”: 4.0},

{“bucket”: 7, “count”: 5, “avg_delay”: 8.8}

]

2. Delay distribution by weekday

GET /analytics/delays/distribution?group_by=weekday

Request:

curl -s “http://127.0.0.1:8000/analytics/delays/distribution?group_by=weekday”

Response (200):

[

{“bucket”: 0, “count”: 4, “avg_delay”: 7.25},

{“bucket”: 1, “count”: 11, “avg_delay”: 8.27}

]

3. Route reliability

GET /analytics/routes/{route_id}/reliability

Definition:

An incident is “on time” if delay_minutes <= threshold_minutes (default 5).

reliability_percent = (on_time_incidents / total_incidents) * 100

Request:

curl -s “http://127.0.0.1:8000/analytics/routes/5/reliability”

Response (200):

{

“route_id”: 5,

“from_date”: null,

“to_date”: null,

“threshold_minutes”: 5,

“total_incidents”: 1,

“on_time_incidents”: 0,

“reliability_percent”: 0.0

}

4. Hotspot stations

GET /analytics/stations/hotspots?window_days=30&limit=10

Definition:

pain_index = incident_count * avg_delay

Request:

curl -s “http://127.0.0.1:8000/analytics/stations/hotspots?window_days=30&limit=10”

Response (200):

{

“window_days”: 30,

“results”: [

{

“station_id”: 1,

“station_name”: “Test Station 1”,

“incident_count”: 36,

“avg_delay”: 9.69,

“pain_index”: 349.0

}

]

}

Error codes and what causes them

401 Unauthorized

* Missing Authorization header for a protected endpoint
* Invalid or expired JWT

403 Forbidden

* Authenticated but not allowed (e.g., editing/deleting an incident created by a different user)

404 Not Found

* Route/station/incident ID does not exist

422 Unprocessable Entity

* Invalid input type or missing required fields (FastAPI validation)

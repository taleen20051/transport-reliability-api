# **Public Transport Reliability & Incident Analytics API**

A data-driven RESTful API designed to analyse public transport reliability using user-reported delay incidents and real UK transport infrastructure data.

This project was developed for the COMP3011 - Web Services and Web Data coursework.

The system combines CRUD operations, authentication, database persistence, and analytical endpoints to evaluate transport reliability and identify operational bottlenecks.

# **Project Overview**

Public transport networks generate large volumes of operational data, yet this information is rarely exposed through structured analytics-ready APIs. Without quantitative reliability metrics and hotspot detection, decision-making remains reactive rather than data-driven.

This project addresses that problem by implementing a **RESTful analytics API** that enables:

* Structured management of transport infrastructure data
* User-reported delay incident tracking
* Quantitative reliability analysis
* Temporal delay pattern analysis
* Station-level hotspot detection

The system is designed using production-oriented backend architecture, prioritising modularity, documentation quality, testing, and reproducibility.

# **Key Features**

## **CRUD Data Management**

The API implements full **Create, Read, Update, Delete** functionality for core entities:

* Routes
* Stations
* UserIncidents

Authenticated users can create, update, and delete incidents while maintaining ownership enforcement.

## **Analytical Endpoints**

Beyond basic CRUD functionality, the API exposes analytical endpoints that compute aggregated transport performance indicators.

### **Route Reliability**

Calculates the percentage of incidents where delays fall below a specified threshold.
GET /analytics/routes/{route_id}/reliability

Example response:

```
{
  "route_id": 8,
  "total_incidents": 12,
  "on_time_incidents": 9,
  "reliability_percent": 75
}
```

### Delay Distribution

Aggregates delays by hour or weekday to identify temporal patterns.

GET /analytics/delays/distribution?group_by=weekday

Example response:

```
[
  {
    "bucket": 0,
    "count": 12,
    "avg_delay": 7.5
  }
]
```

### Station Hotspots

Identifies stations with the highest operational disruption.

`GET /analytics/stations/hotspots`

Stations are ranked using the metric:

`pain_index = incident_count × average_delay`

This balances frequency and severity of disruptions.

# **Technology Stack**

| **Layer**      | **Technology**  |
| -------------------- | --------------------- |
| Programming Language | Python                |
| API Framework        | FastAPI               |
| Database             | PostgreSQL            |
| ORM                  | SQLAlchemy            |
| Database Migrations  | Alembic               |
| Authentication       | JWT (JSON Web Tokens) |
| Validation           | Pydantic              |
| Testing              | Pytest                |
| API Documentation    | OpenAPI / Swagger UI  |

FastAPI was selected for its automatic OpenAPI documentation, strong validation system, and dependency injection support, enabling clean API design and maintainability.

# System Architecture

The API follows a layered architecture separating HTTP routing, business logic, and persistence.

Client / HTTP Requests -> FastAPI Routers (API Layer) -> Service Layer (Business Logic) -> Persistence Layer (SQLAlchemy ORM) -> PostgreSQL Database

This structure ensures:

* separation of concerns
* maintainability
* modular code organisation
* easier testing and scalability

# **Repository Structure**

## transport-reliability-api

│
├── app
│   ├── routers        # API endpoint definitions
│   ├── schemas        # Pydantic request/response models
│   ├── models         # SQLAlchemy database models
│   ├── services       # Business logic & analytics computations
│   ├── auth           # Authentication utilities
│   └── db             # Database configuration
│
├── scripts            # Dataset ingestion scripts
├── tests              # Pytest integration tests
├── alembic            # Database migration configuration
│
├── API_Documentation.pdf
├── README.md
└── requirements.txt

# Setup Instructions

## 1/ Clone the repository

git clone https://github.com/YOUR_USERNAME/transport-reliability-api.git

cd transport-reliability-api

## 2/ Create the environment

python -m venv .venv
source .venv/bin/activate

Windows: .venv\Scripts\activate

## 3/ Install Dependencies

pip install -r requirements.txt

# Environment Variables

Create a .env file in the project root.

Example configuration:

`DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/transport_db `

`SECRET_KEY=change_this_secret_key `

`ALGORITHM=HS256 `

`ACCESS_TOKEN_EXPIRE_MINUTES=60`

These variables configure the database connection and JWT authentication system.

# **Database Setup**

Run Alembic migrations to create the database schema.

    alembic upgrade head

This initialises all required database tables.

# Dataset Import

The system integrates real UK transport infrastructure data from the NaPTAN dataset (National Public Transport Access Nodes).

To import station data:

    python scripts/import_naptan_stations.py

The import process:

* parses CSV dataset entries
* validates coordinate values
* skips invalid rows
* prevents duplicate entries
* inserts a controlled subset for demonstration purposes

# **Running the API**

Start the development server using Uvicorn.

`uvicorn app.main:app --reload`

The API will run locally at:

`http://127.0.0.1:8000`

# API Documentation

Interactive API documentation is automatically generated using OpenAPI / Swagger UI.

Access documentation at: http://127.0.0.1:8000/docs

This interface provides:

    •	endpoint descriptions

    •	parameter specifications

    •	example requests

    •	example responses

    •	authentication support

A static PDF version of the documentation is also included in this repository: API_Documentation.pdf

# **Authentication**

The API uses **JWT (JSON Web Token) authentication** **.**

## **Register**

`POST /auth/register`

Example request:

```
{
  "email": "user@example.com",
  "password": "StrongPass123"
}
```

## **Login**

POST /auth/login

Example response:

`{
  "access_token": "<jwt_token>",
  "token_type": "bearer"
}`

Include the token in protected requests: Authorization: Bearer <access_token>

# **Error Handling**

The API uses standard HTTP status codes.

| **Code** | **Meaning**  |
| -------------- | ------------------ |
| 200            | Successful request |
| 201            | Resource created   |
| 204            | Resource deleted   |
| 400            | Bad request        |
| 401            | Unauthorized       |
| 403            | Forbidden          |
| 404            | Resource not found |
| 422            | Validation error   |

Ownership enforcement ensures users can only modify incidents they created.

# **Testing**

Testing is implemented using pytest with an isolated test database.

Test coverage includes:

* CRUD endpoint behaviour
* authentication flows
* ownership enforcement
* validation errors
* analytics aggregation logic

Run tests using: pytest

# **Generative AI Usage**

Generative AI tools (ChatGPT and Gemini) were used to assist with:

* architectural design exploration
* API framework comparison
* dataset ingestion strategy
* documentation refinement
* debugging guidance

All generated outputs were reviewed, adapted, and validated independently before integration into the project.

Representative conversation excerpts are included in the technical report appendix.

# **Coursework Deliverables**

This repository contains all required coursework deliverables:

* version-controlled source code
* API documentation (PDF)
* technical report
* presentation slides
* dataset ingestion scripts
* automated test suite

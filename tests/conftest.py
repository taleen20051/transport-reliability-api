# Shared pytest fixtures and helper functions used across the API test suite

import os
import sys
import uuid
from pathlib import Path

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()
# Ensure the application package can be imported when tests are run from the project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.db.base import Base
from app.db.deps import get_db


# Resolve the database URL for tests, preferring a dedicated test database if available
@pytest.fixture(scope="session")
def test_database_url() -> str:
    url = os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "Set TEST_DATABASE_URL (recommended) or DATABASE_URL before running tests."
        )
    return url


# Create one SQLAlchemy engine for the test session
@pytest.fixture(scope="session")
def engine(test_database_url: str):
    return create_engine(test_database_url, pool_pre_ping=True)


# Build a reusable session factory bound to the test engine
@pytest.fixture(scope="session")
def TestingSessionLocal(engine):
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)


# Create all tables before the test session starts and remove them afterwards
@pytest.fixture(scope="session", autouse=True)
def create_test_tables(engine):
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# Provide an isolated database session for individual tests
@pytest.fixture()
def db_session(TestingSessionLocal):
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override the application's database dependency so API requests use the test database
@pytest.fixture()
def client(TestingSessionLocal):
    from app.main import app

    # Yield a test-scoped database session instead of the production dependency
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# Generate a unique email address to avoid collisions between test runs
def unique_email(prefix="user") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:10]}@example.com"


# Helper to create a user through the public registration endpoint
def register_user(client: TestClient, email: str, password: str = "StrongPass123"):
    r = client.post("/auth/register", json={"email": email, "password": password})
    assert r.status_code == 201, r.text
    return r.json()


# Helper to authenticate a user and return a valid access token
def login_user(client: TestClient, email: str, password: str = "StrongPass123") -> str:
    r = client.post(
        "/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


# Build the Authorization header expected by protected endpoints
def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# Helper to create a route using an authenticated request
def create_route(client: TestClient, token: str, name="Test Route"):
    r = client.post(
        "/routes",
        json={"name": name, "mode": "bus", "operator": "Test Operator"},
        headers=auth_header(token),
    )
    assert r.status_code == 201, r.text
    return r.json()


# Helper to create a station using an authenticated request
def create_station(client: TestClient, token: str, name="Test Station"):
    r = client.post(
        "/stations",
        json={"name": name, "lat": 53.8, "lon": -1.55},
        headers=auth_header(token),
    )
    assert r.status_code == 201, r.text
    return r.json()


# Helper to create a sample incident for CRUD and analytics tests
def create_incident(client: TestClient, token: str, route_id: int, station_id: int | None = None):
    payload = {
        "route_id": route_id,
        "station_id": station_id,
        "delay_minutes": 12,
        "category": "delay",
        "description": "Test incident",
    }
    r = client.post("/incidents", json=payload, headers=auth_header(token))
    assert r.status_code == 201, r.text
    return r.json()
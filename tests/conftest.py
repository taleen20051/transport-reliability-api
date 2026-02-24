import os
import sys
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# --- Ensure project root is on PYTHONPATH so `import app...` works ---
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.db.base import Base  # noqa: E402
from app.db.deps import get_db  # noqa: E402


@pytest.fixture(scope="session")
def test_database_url() -> str:
    """
    Uses TEST_DATABASE_URL if set; otherwise falls back to DATABASE_URL.
    """
    url = os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "Set TEST_DATABASE_URL (recommended) or DATABASE_URL before running tests."
        )
    return url


@pytest.fixture(scope="session")
def engine(test_database_url: str):
    """
    Create a SQLAlchemy engine for the test database.
    """
    return create_engine(test_database_url, pool_pre_ping=True)


@pytest.fixture(scope="session")
def TestingSessionLocal(engine):
    """
    Create a sessionmaker bound to the test engine.
    """
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture(scope="session", autouse=True)
def create_test_tables(engine):
    """
    Create all tables once per test session, drop at end.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session(TestingSessionLocal):
    """
    New DB session per test.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(TestingSessionLocal):
    """
    FastAPI TestClient with get_db dependency overridden to use test DB.
    """
    from app.main import app  # import here so overrides apply cleanly

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


def unique_email(prefix="user") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:10]}@example.com"


def register_user(client: TestClient, email: str, password: str = "StrongPass123"):
    r = client.post("/auth/register", json={"email": email, "password": password})
    assert r.status_code == 201, r.text
    return r.json()


def login_user(client: TestClient, email: str, password: str = "StrongPass123") -> str:
    r = client.post(
        "/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def create_route(client: TestClient, token: str, name="Test Route"):
    r = client.post(
        "/routes",
        json={"name": name, "mode": "bus", "operator": "Test Operator"},
        headers=auth_header(token),
    )
    assert r.status_code == 201, r.text
    return r.json()


def create_station(client: TestClient, token: str, name="Test Station"):
    r = client.post(
        "/stations",
        json={"name": name, "lat": 53.8, "lon": -1.55},
        headers=auth_header(token),
    )
    assert r.status_code == 201, r.text
    return r.json()


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
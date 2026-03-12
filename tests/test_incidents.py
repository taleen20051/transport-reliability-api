# Integration tests covering protected incident CRUD behaviour, ownership rules,
# validation, and foreign-key checks

from tests.conftest import (
    unique_email,
    register_user,
    login_user,
    auth_header,
    create_route,
    create_station,
    create_incident,
)


# Confirm that incident creation is blocked for unauthenticated requests
def test_incidents_requires_auth_on_create(client):
    r = client.post(
        "/incidents",
        json={
            "route_id": 1,
            "station_id": None,
            "delay_minutes": 5,
            "category": "delay",
            "description": "No auth",
        },
    )
    assert r.status_code == 401


# Incident update should require authentication
def test_incidents_requires_auth_on_patch(client):
    r = client.patch("/incidents/1", json={"delay_minutes": 20})
    assert r.status_code == 401


# Incident delete should require authentication
def test_incidents_requires_auth_on_delete(client):
    r = client.delete("/incidents/1")
    assert r.status_code == 401


# Confirm that the incident owner can create, read, update, and delete their own incident
def test_incident_crud_owner_can_update_and_delete(client):
    email = unique_email("inc-owner")
    register_user(client, email)
    token = login_user(client, email)

    route = create_route(client, token, name="Owner Route")
    station = create_station(client, token, name="Owner Station")

    incident = create_incident(client, token, route_id=route["id"], station_id=station["id"])
    iid = incident["id"]

    r = client.get(f"/incidents/{iid}")
    assert r.status_code == 200
    assert r.json()["id"] == iid

    r = client.patch(
        f"/incidents/{iid}",
        json={"delay_minutes": 20, "description": "Updated delay test"},
        headers=auth_header(token),
    )
    assert r.status_code == 200
    assert r.json()["delay_minutes"] == 20
    assert r.json()["description"] == "Updated delay test"

    r = client.delete(f"/incidents/{iid}", headers=auth_header(token))
    assert r.status_code == 204

    r = client.get(f"/incidents/{iid}")
    assert r.status_code == 404


# Confirm that a different authenticated user cannot modify another user's incident
def test_incident_patch_forbidden_for_non_owner(client):
    email1 = unique_email("u1")
    register_user(client, email1)
    token1 = login_user(client, email1)

    route = create_route(client, token1, name="Route Shared")
    incident = create_incident(client, token1, route_id=route["id"], station_id=None)
    iid = incident["id"]

    email2 = unique_email("u2")
    register_user(client, email2)
    token2 = login_user(client, email2)

    r = client.patch(
        f"/incidents/{iid}",
        json={"delay_minutes": 99},
        headers=auth_header(token2),
    )
    assert r.status_code == 403
    assert r.json()["detail"] == "Not allowed"


# Confirm that a different authenticated user cannot delete another user's incident
def test_incident_delete_forbidden_for_non_owner(client):
    email1 = unique_email("u1del")
    register_user(client, email1)
    token1 = login_user(client, email1)

    route = create_route(client, token1, name="Delete Shared Route")
    incident = create_incident(client, token1, route_id=route["id"], station_id=None)
    iid = incident["id"]

    email2 = unique_email("u2del")
    register_user(client, email2)
    token2 = login_user(client, email2)

    r = client.delete(f"/incidents/{iid}", headers=auth_header(token2))
    assert r.status_code == 403
    assert r.json()["detail"] == "Not allowed"


# Invalid incident IDs should return 404 when retrieved
def test_get_incident_not_found(client):
    r = client.get("/incidents/999999")
    assert r.status_code == 404


# Invalid incident IDs should return 404 when patched
def test_patch_incident_not_found(client):
    email = unique_email("inc404patch")
    register_user(client, email)
    token = login_user(client, email)

    r = client.patch(
        "/incidents/999999",
        json={"delay_minutes": 50},
        headers=auth_header(token),
    )
    assert r.status_code == 404


# Invalid incident IDs should return 404 when deleted
def test_delete_incident_not_found(client):
    email = unique_email("inc404delete")
    register_user(client, email)
    token = login_user(client, email)

    r = client.delete("/incidents/999999", headers=auth_header(token))
    assert r.status_code == 404


# Creating an incident with a missing route should return 404 rather than a 500
def test_create_incident_invalid_route_returns_404(client):
    email = unique_email("badroute")
    register_user(client, email)
    token = login_user(client, email)

    station = create_station(client, token, name="Station For Bad Route")

    r = client.post(
        "/incidents",
        json={
            "route_id": 999999,
            "station_id": station["id"],
            "delay_minutes": 12,
            "category": "delay",
            "description": "Bad route",
        },
        headers=auth_header(token),
    )
    assert r.status_code == 404
    assert r.json()["detail"] == "Route not found"


# Creating an incident with a missing station should return 404
def test_create_incident_invalid_station_returns_404(client):
    email = unique_email("badstation")
    register_user(client, email)
    token = login_user(client, email)

    route = create_route(client, token, name="Route For Bad Station")

    r = client.post(
        "/incidents",
        json={
            "route_id": route["id"],
            "station_id": 999999,
            "delay_minutes": 12,
            "category": "delay",
            "description": "Bad station",
        },
        headers=auth_header(token),
    )
    assert r.status_code == 404
    assert r.json()["detail"] == "Station not found"


# Invalid incident payloads should fail schema validation
def test_create_incident_validation_error(client):
    email = unique_email("inc422")
    register_user(client, email)
    token = login_user(client, email)

    route = create_route(client, token, name="Validation Route")

    # Missing category and description
    r = client.post(
        "/incidents",
        json={
            "route_id": route["id"],
            "station_id": None,
            "delay_minutes": 12,
        },
        headers=auth_header(token),
    )
    assert r.status_code == 422
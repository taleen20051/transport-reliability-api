# Integration tests covering protected incident CRUD behaviour and ownership rules

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
def test_incidents_requires_auth(client):
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

    r = client.patch(
        f"/incidents/{iid}",
        json={"delay_minutes": 20},
        headers=auth_header(token),
    )
    assert r.status_code == 200
    assert r.json()["delay_minutes"] == 20

    r = client.delete(f"/incidents/{iid}", headers=auth_header(token))
    assert r.status_code == 204

    r = client.get(f"/incidents/{iid}")
    assert r.status_code == 404


# Confirm that a different authenticated user cannot modify another user's incident
def test_incident_ownership_forbidden(client):
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
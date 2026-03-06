# Tests covering protected route creation and route retrieval

from tests.conftest import unique_email, register_user, login_user, auth_header


# Route creation should require authentication
def test_routes_requires_auth(client):
    r = client.post("/routes", json={"name": "NoAuth Route", "mode": "bus", "operator": "X"})
    assert r.status_code == 401


# Verify that an authenticated user can create a route and retrieve it afterwards
def test_create_and_get_route(client):
    email = unique_email("routes")
    register_user(client, email)
    token = login_user(client, email)

    r = client.post(
        "/routes",
        json={"name": "Route A", "mode": "bus", "operator": "Test"},
        headers=auth_header(token),
    )
    assert r.status_code == 201
    route = r.json()
    assert "id" in route

    rid = route["id"]
    r = client.get(f"/routes/{rid}")
    assert r.status_code == 200
    got = r.json()
    assert got["id"] == rid
    assert got["name"] == "Route A"
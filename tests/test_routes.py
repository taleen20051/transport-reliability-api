# Tests covering full route CRUD behaviour, auth protection, and validation

from tests.conftest import unique_email, register_user, login_user, auth_header


# Route creation should require authentication
def test_routes_requires_auth_on_create(client):
    r = client.post("/routes", json={"name": "NoAuth Route", "mode": "bus", "operator": "X"})
    assert r.status_code == 401


# Route update should require authentication
def test_routes_requires_auth_on_patch(client):
    r = client.patch("/routes/1", json={"name": "Updated Without Auth"})
    assert r.status_code == 401


# Route deletion should require authentication
def test_routes_requires_auth_on_delete(client):
    r = client.delete("/routes/1")
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
    rid = route["id"]

    r = client.get(f"/routes/{rid}")
    assert r.status_code == 200
    got = r.json()
    assert got["id"] == rid
    assert got["name"] == "Route A"
    assert got["mode"] == "bus"
    assert got["operator"] == "Test"


# Listing routes should return a JSON list
def test_list_routes(client):
    r = client.get("/routes?limit=10&offset=0")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


# Invalid route IDs should return 404 rather than crashing
def test_get_route_not_found(client):
    r = client.get("/routes/999999")
    assert r.status_code == 404


# Verify route details can be partially updated
def test_patch_route(client):
    email = unique_email("routespatch")
    register_user(client, email)
    token = login_user(client, email)

    r = client.post(
        "/routes",
        json={"name": "Patch Me", "mode": "bus", "operator": "Old Operator"},
        headers=auth_header(token),
    )
    assert r.status_code == 201
    rid = r.json()["id"]

    r = client.patch(
        f"/routes/{rid}",
        json={"name": "Patched Route", "operator": "New Operator"},
        headers=auth_header(token),
    )
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "Patched Route"
    assert body["operator"] == "New Operator"

    r = client.get(f"/routes/{rid}")
    assert r.status_code == 200
    assert r.json()["name"] == "Patched Route"


# Patching a route that does not exist should return 404
def test_patch_route_not_found(client):
    email = unique_email("routespatch404")
    register_user(client, email)
    token = login_user(client, email)

    r = client.patch(
        "/routes/999999",
        json={"name": "Does Not Exist"},
        headers=auth_header(token),
    )
    assert r.status_code == 404


# Verify a route can be deleted and is no longer retrievable afterwards
def test_delete_route(client):
    email = unique_email("routesdelete")
    register_user(client, email)
    token = login_user(client, email)

    r = client.post(
        "/routes",
        json={"name": "Delete Me", "mode": "bus", "operator": "Delete Operator"},
        headers=auth_header(token),
    )
    assert r.status_code == 201
    rid = r.json()["id"]

    r = client.delete(f"/routes/{rid}", headers=auth_header(token))
    assert r.status_code == 204

    r = client.get(f"/routes/{rid}")
    assert r.status_code == 404


# Deleting a route that does not exist should return 404
def test_delete_route_not_found(client):
    email = unique_email("routesdelete404")
    register_user(client, email)
    token = login_user(client, email)

    r = client.delete("/routes/999999", headers=auth_header(token))
    assert r.status_code == 404


# Invalid route payloads should fail validation
def test_create_route_validation_error(client):
    email = unique_email("routes422")
    register_user(client, email)
    token = login_user(client, email)

    # Missing required name field
    r = client.post(
        "/routes",
        json={"mode": "bus", "operator": "Test"},
        headers=auth_header(token),
    )
    assert r.status_code == 422
# Tests covering full station CRUD behaviour, auth protection, and validation

from tests.conftest import unique_email, register_user, login_user, auth_header


# Station creation should require authentication
def test_stations_requires_auth_on_create(client):
    r = client.post("/stations", json={"name": "NoAuth Station", "lat": 1.0, "lon": 2.0})
    assert r.status_code == 401


# Station update should require authentication
def test_stations_requires_auth_on_patch(client):
    r = client.patch("/stations/1", json={"name": "Updated Without Auth"})
    assert r.status_code == 401


# Station deletion should require authentication
def test_stations_requires_auth_on_delete(client):
    r = client.delete("/stations/1")
    assert r.status_code == 401


# Verify that an authenticated user can create a station and retrieve it afterwards
def test_create_and_get_station(client):
    email = unique_email("stations")
    register_user(client, email)
    token = login_user(client, email)

    r = client.post(
        "/stations",
        json={"name": "Leeds Station", "lat": 53.8, "lon": -1.55},
        headers=auth_header(token),
    )
    assert r.status_code == 201
    station = r.json()
    sid = station["id"]

    r = client.get(f"/stations/{sid}")
    assert r.status_code == 200
    got = r.json()
    assert got["id"] == sid
    assert got["name"] == "Leeds Station"


# Listing stations should return a JSON list
def test_list_stations(client):
    r = client.get("/stations?limit=10&offset=0")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


# Invalid station IDs should return 404
def test_get_station_not_found(client):
    r = client.get("/stations/999999")
    assert r.status_code == 404


# Verify station details can be updated
def test_patch_station(client):
    email = unique_email("stationspatch")
    register_user(client, email)
    token = login_user(client, email)

    r = client.post(
        "/stations",
        json={"name": "Old Station", "lat": 53.8, "lon": -1.55},
        headers=auth_header(token),
    )
    assert r.status_code == 201
    sid = r.json()["id"]

    r = client.patch(
        f"/stations/{sid}",
        json={"name": "Updated Station", "lat": 54.0},
        headers=auth_header(token),
    )
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "Updated Station"
    assert body["lat"] == 54.0


# Patching a missing station should return 404
def test_patch_station_not_found(client):
    email = unique_email("stationspatch404")
    register_user(client, email)
    token = login_user(client, email)

    r = client.patch(
        "/stations/999999",
        json={"name": "No Such Station"},
        headers=auth_header(token),
    )
    assert r.status_code == 404


# Verify a station can be deleted and disappears afterwards
def test_delete_station(client):
    email = unique_email("stationsdelete")
    register_user(client, email)
    token = login_user(client, email)

    r = client.post(
        "/stations",
        json={"name": "Delete Station", "lat": 53.8, "lon": -1.55},
        headers=auth_header(token),
    )
    assert r.status_code == 201
    sid = r.json()["id"]

    r = client.delete(f"/stations/{sid}", headers=auth_header(token))
    assert r.status_code == 204

    r = client.get(f"/stations/{sid}")
    assert r.status_code == 404


# Deleting a missing station should return 404
def test_delete_station_not_found(client):
    email = unique_email("stationsdelete404")
    register_user(client, email)
    token = login_user(client, email)

    r = client.delete("/stations/999999", headers=auth_header(token))
    assert r.status_code == 404


# Invalid station payloads should fail validation
def test_create_station_validation_error(client):
    email = unique_email("stations422")
    register_user(client, email)
    token = login_user(client, email)

    # Missing required name field
    r = client.post(
        "/stations",
        json={"lat": 53.8, "lon": -1.55},
        headers=auth_header(token),
    )
    assert r.status_code == 422
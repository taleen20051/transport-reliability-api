# Tests covering protected station creation and station retrieval

from tests.conftest import unique_email, register_user, login_user, auth_header


# Station creation should require authentication
def test_stations_requires_auth(client):
    r = client.post("/stations", json={"name": "NoAuth Station", "lat": 1.0, "lon": 2.0})
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
    assert got["name"] == "Leeds Station"
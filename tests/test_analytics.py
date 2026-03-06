# Integration tests covering analytics endpoints and aggregated API behaviour

from tests.conftest import (
    unique_email,
    register_user,
    login_user,
    create_route,
    create_station,
    create_incident,
)


# Verify that delay distribution works for both supported grouping dimensions
def test_delay_distribution_hour_and_weekday(client):
    email = unique_email("analytics")
    register_user(client, email)
    token = login_user(client, email)

    # Seed minimal data so the analytics endpoint has at least one incident to aggregate
    route = create_route(client, token, name="Analytics Route")
    station = create_station(client, token, name="Analytics Station")
    create_incident(client, token, route_id=route["id"], station_id=station["id"])

    r = client.get("/analytics/delays/distribution?group_by=hour")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

    r = client.get("/analytics/delays/distribution?group_by=weekday")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


# Verify that the route reliability endpoint returns the expected summary fields
def test_route_reliability(client):
    email = unique_email("reliability")
    register_user(client, email)
    token = login_user(client, email)

    route = create_route(client, token, name="Reliability Route")
    create_incident(client, token, route_id=route["id"], station_id=None)

    r = client.get(f"/analytics/routes/{route['id']}/reliability")
    assert r.status_code == 200
    body = r.json()
    assert body["route_id"] == route["id"]
    assert "reliability_percent" in body
    assert "total_incidents" in body


# Verify that hotspot station analytics return a structured list of ranked results
def test_hotspot_stations(client):
    email = unique_email("hotspots")
    register_user(client, email)
    token = login_user(client, email)

    route = create_route(client, token, name="Hotspot Route")
    station = create_station(client, token, name="Hotspot Station")
    create_incident(client, token, route_id=route["id"], station_id=station["id"])

    r = client.get("/analytics/stations/hotspots?window_days=30&limit=10")
    assert r.status_code == 200
    body = r.json()
    assert "results" in body
    assert isinstance(body["results"], list)
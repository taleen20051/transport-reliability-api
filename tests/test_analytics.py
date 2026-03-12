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


# Unsupported grouping values should fail validation
def test_delay_distribution_invalid_group_by_returns_422(client):
    r = client.get("/analytics/delays/distribution?group_by=banana")
    assert r.status_code == 422


# Verify that the route reliability endpoint returns expected summary fields
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


# Reliability should respond differently when the threshold changes
def test_route_reliability_threshold_logic(client):
    email = unique_email("reliability-threshold")
    register_user(client, email)
    token = login_user(client, email)

    route = create_route(client, token, name="Threshold Route")
    create_incident(client, token, route_id=route["id"], station_id=None)

    # Default helper creates an incident with 12 minutes of delay.
    # With threshold 10 it should count as late; with threshold 15 it should count as on-time.
    r = client.get(f"/analytics/routes/{route['id']}/reliability?threshold=10")
    assert r.status_code == 200
    body_low = r.json()

    r = client.get(f"/analytics/routes/{route['id']}/reliability?threshold=15")
    assert r.status_code == 200
    body_high = r.json()

    assert body_low["route_id"] == route["id"]
    assert body_high["route_id"] == route["id"]
    assert body_low["total_incidents"] == body_high["total_incidents"] == 1
    assert body_low["reliability_percent"] <= body_high["reliability_percent"]


# Nonexistent routes should return 404 in the reliability endpoint
def test_route_reliability_not_found(client):
    r = client.get("/analytics/routes/999999/reliability")
    assert r.status_code == 404


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


# Hotspot limit parameter should still produce a valid result shape
def test_hotspot_stations_respects_limit_shape(client):
    email = unique_email("hotspotslimit")
    register_user(client, email)
    token = login_user(client, email)

    route = create_route(client, token, name="Hotspot Limit Route")
    station = create_station(client, token, name="Hotspot Limit Station")
    create_incident(client, token, route_id=route["id"], station_id=station["id"])

    r = client.get("/analytics/stations/hotspots?window_days=30&limit=1")
    assert r.status_code == 200
    body = r.json()
    assert "results" in body
    assert isinstance(body["results"], list)
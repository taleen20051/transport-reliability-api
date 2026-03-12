# Tests covering user registration, login, and authentication failure cases

from tests.conftest import unique_email, auth_header

# Ensure a user can register successfully and then obtain a JWT access token
def test_register_and_login(client):
    email = unique_email("auth")
    password = "StrongPass123"

    r = client.post("/auth/register", json={"email": email, "password": password})
    assert r.status_code == 201
    body = r.json()
    assert "id" in body
    assert body["email"] == email

    r = client.post(
        "/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200
    body = r.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


# Duplicate email registration should fail rather than silently creating another account
def test_register_duplicate_email_fails(client):
    email = unique_email("dup")
    password = "StrongPass123"

    r = client.post("/auth/register", json={"email": email, "password": password})
    assert r.status_code == 201

    r = client.post("/auth/register", json={"email": email, "password": password})
    assert r.status_code in (400, 409)


# Login with the wrong password should be rejected
def test_login_wrong_password_fails(client):
    email = unique_email("wrongpw")
    password = "StrongPass123"

    r = client.post("/auth/register", json={"email": email, "password": password})
    assert r.status_code == 201

    r = client.post(
        "/auth/login",
        data={"username": email, "password": "WrongPassword999"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 401


# Login for a user that does not exist should also be rejected
def test_login_unknown_user_fails(client):
    r = client.post(
        "/auth/login",
        data={"username": "doesnotexist@example.com", "password": "StrongPass123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 401


# Protected endpoints should reject malformed bearer tokens
def test_protected_endpoint_rejects_bad_token(client):
    r = client.post(
        "/routes",
        json={"name": "Bad Token Route", "mode": "bus", "operator": "X"},
        headers=auth_header("not-a-real-token"),
    )
    assert r.status_code == 401
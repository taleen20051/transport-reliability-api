from tests.conftest import unique_email


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
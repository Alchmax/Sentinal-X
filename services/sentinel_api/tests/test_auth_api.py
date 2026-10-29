def test_register_login(client):
    r = client.post(
        "/api/v1/auth/register",
        json={"email": "a@b.com", "password": "secret123", "full_name": "A"},
    )
    assert r.status_code == 200
    token = r.json()["access_token"]
    r2 = client.post(
        "/api/v1/auth/login", json={"email": "a@b.com", "password": "secret123"}
    )
    assert r2.status_code == 200
    # protected
    r3 = client.get("/api/v1/cases", headers={"Authorization": f"Bearer {token}"})
    assert r3.status_code == 200


def test_unauth_cases(client):
    r = client.get("/api/v1/cases")
    assert r.status_code == 401

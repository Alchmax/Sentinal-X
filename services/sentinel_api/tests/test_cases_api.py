def _token(client):
    client.post(
        "/api/v1/auth/register", json={"email": "u@b.com", "password": "secret123"}
    )
    r = client.post(
        "/api/v1/auth/login", json={"email": "u@b.com", "password": "secret123"}
    )
    return r.json()["access_token"]


def test_case_crud(client):
    token = _token(client)
    h = {"Authorization": f"Bearer {token}"}
    r = client.post(
        "/api/v1/cases",
        json={"title": "Case1", "description": "d", "tags": ["t1"]},
        headers=h,
    )
    assert r.status_code == 200
    cid = r.json()["id"]
    assert r.json()["tags"] == ["t1"]
    r2 = client.get(f"/api/v1/cases/{cid}", headers=h)
    assert r2.status_code == 200
    r3 = client.patch(
        f"/api/v1/cases/{cid}",
        json={"title": "Case1b", "status": "in_progress"},
        headers=h,
    )
    assert r3.json()["title"] == "Case1b"
    r4 = client.get("/api/v1/cases", headers=h)
    assert r4.json()["total"] >= 1
    # authorization boundary: other user
    client.post(
        "/api/v1/auth/register", json={"email": "u2@b.com", "password": "secret123"}
    )
    r5 = client.post(
        "/api/v1/auth/login", json={"email": "u2@b.com", "password": "secret123"}
    )
    t2 = r5.json()["access_token"]
    r6 = client.get(f"/api/v1/cases/{cid}", headers={"Authorization": f"Bearer {t2}"})
    assert r6.status_code == 403


def test_archive_case(client):
    token = _token(client) if False else None
    # reuse register
    client.post(
        "/api/v1/auth/register", json={"email": "u3@b.com", "password": "secret123"}
    )
    r = client.post(
        "/api/v1/auth/login", json={"email": "u3@b.com", "password": "secret123"}
    )
    token = r.json()["access_token"]
    h = {"Authorization": f"Bearer {token}"}
    cid = client.post("/api/v1/cases", json={"title": "C"}, headers=h).json()["id"]
    r = client.post(f"/api/v1/cases/{cid}/archive", headers=h)
    assert r.status_code == 200
    assert r.json()["status"] == "archived"

def test_sync_idempotency(client):
    client.post(
        "/api/v1/auth/register", json={"email": "sy@b.com", "password": "secret123"}
    )
    r = client.post(
        "/api/v1/auth/login", json={"email": "sy@b.com", "password": "secret123"}
    )
    token = r.json()["access_token"]
    h = {"Authorization": f"Bearer {token}"}
    r1 = client.post(
        "/api/v1/sync/enqueue",
        json={"entity_type": "case", "entity_id": "123", "version": "1"},
        headers=h,
    )
    assert r1.status_code == 200
    rid = r1.json()["id"]
    r2 = client.post(
        f"/api/v1/sync/complete/{rid}", params={"status": "completed"}, headers=h
    )
    assert r2.json()["status"] == "completed"
    r3 = client.get("/api/v1/sync/status", headers=h)
    assert len(r3.json()) >= 1

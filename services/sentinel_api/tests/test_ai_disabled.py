def test_ai_status_disabled(client):
    r = client.get("/api/v1/ai/status")
    assert r.status_code == 200
    data = r.json()
    assert data["enabled"] is False
    assert data["configured"] is False


def test_ai_chat_requires_approval(client):
    # register
    client.post(
        "/api/v1/auth/register", json={"email": "ai@b.com", "password": "secret123"}
    )
    r = client.post(
        "/api/v1/auth/login", json={"email": "ai@b.com", "password": "secret123"}
    )
    token = r.json()["access_token"]
    h = {"Authorization": f"Bearer {token}"}
    cid = client.post("/api/v1/cases", json={"title": "C"}, headers=h).json()["id"]
    r2 = client.post(
        "/api/v1/ai/chat",
        json={"case_id": cid, "question": "summarize", "approved": False},
        headers=h,
    )
    assert r2.status_code == 200
    assert r2.json()["error"] == "Context must be approved before transmission"

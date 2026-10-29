def test_report_generation(client):
    client.post(
        "/api/v1/auth/register", json={"email": "rep@b.com", "password": "secret123"}
    )
    r = client.post(
        "/api/v1/auth/login", json={"email": "rep@b.com", "password": "secret123"}
    )
    token = r.json()["access_token"]
    h = {"Authorization": f"Bearer {token}"}
    cid = client.post("/api/v1/cases", json={"title": "C"}, headers=h).json()["id"]
    # add evidence via analyze? register with upload
    import io

    files = {"file": ("a.txt", io.BytesIO(b"hello"), "text/plain")}
    data = {"case_id": cid}
    client.post("/api/v1/evidence/register", data=data, files=files, headers=h)
    # build timeline
    client.post(f"/api/v1/timeline/build/{cid}", headers=h)
    r2 = client.post(f"/api/v1/reports/generate/{cid}?format=html", headers=h)
    assert r2.status_code == 200
    content = r2.json()["content"]
    assert "SENTINEL X Investigation Report" in content
    assert "a.txt" in content

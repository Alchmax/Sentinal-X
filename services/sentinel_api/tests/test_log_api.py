import io


def test_log_import_and_detect(client):
    client.post(
        "/api/v1/auth/register", json={"email": "lg@b.com", "password": "secret123"}
    )
    r = client.post(
        "/api/v1/auth/login", json={"email": "lg@b.com", "password": "secret123"}
    )
    token = r.json()["access_token"]
    h = {"Authorization": f"Bearer {token}"}
    cid = client.post("/api/v1/cases", json={"title": "C"}, headers=h).json()["id"]
    csv_content = "timestamp,actor,event_type,message\n"
    for i in range(6):
        csv_content += f"2024-01-01T00:0{i}:00Z,alice,login failed,invalid password\n"
    csv_content += "2024-01-01T00:07:00Z,alice,login,login successful\n"
    files = {"file": ("log.csv", io.BytesIO(csv_content.encode()), "text/csv")}
    data = {"case_id": cid}
    imp = client.post("/api/v1/log-analysis/import", data=data, files=files, headers=h)
    assert imp.status_code == 200
    assert imp.json()["parsed"] == 7
    dets = client.post(f"/api/v1/log-analysis/detect/{cid}", headers=h)
    assert dets.status_code == 200
    assert len(dets.json()) >= 1
    # timeline build
    client.post(f"/api/v1/timeline/build/{cid}", headers=h)
    tl = client.get(f"/api/v1/timeline/{cid}", headers=h)
    assert tl.status_code == 200
    assert len(tl.json()) >= 7

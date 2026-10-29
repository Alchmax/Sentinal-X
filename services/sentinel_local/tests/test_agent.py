import os, tempfile, hashlib
from fastapi.testclient import TestClient
from sentinel_agent.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_hash():
    content = b"local test"
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(content)
        path = f.name
    try:
        r = client.post("/hash", json={"path": path})
        assert r.status_code == 200
        assert r.json()["sha256"] == hashlib.sha256(content).hexdigest()
    finally:
        os.remove(path)

def test_hash_missing():
    r = client.post("/hash", json={"path": "C:\\nope\\missing.txt"})
    assert r.status_code == 404
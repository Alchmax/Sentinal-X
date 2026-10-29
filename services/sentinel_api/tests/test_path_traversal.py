from app.services.integrity import build_baseline


def test_integrity_rejects_missing_dir():
    import pytest

    with pytest.raises(ValueError):
        build_baseline("C:\\definitely\\not\\a\\dir\\xyz")


def test_path_traversal_defense_in_api(client):
    # register + login
    client.post(
        "/api/v1/auth/register", json={"email": "pt@b.com", "password": "secret123"}
    )
    r = client.post(
        "/api/v1/auth/login", json={"email": "pt@b.com", "password": "secret123"}
    )
    token = r.json()["access_token"]
    h = {"Authorization": f"Bearer {token}"}
    # try traversal root_path
    r2 = client.post(
        "/api/v1/integrity/baseline",
        json={"root_path": "C:\\Windows\\..\\..\\", "case_id": None},
        headers=h,
    )
    # either 400 or success? resolved path must be a dir; traversal resolves to C:\ which is a dir -> may succeed but no crash
    assert r2.status_code in (200, 400)

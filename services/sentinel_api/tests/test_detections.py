from datetime import UTC, datetime, timedelta

from app.services import detections


def make_events():
    base = datetime(2024, 1, 1, tzinfo=UTC)
    evs = []
    for i in range(6):
        evs.append(
            {
                "id": f"f{i}",
                "timestamp": base + timedelta(minutes=i),
                "actor": "alice",
                "event_type": "login",
                "severity": "error",
                "message": "login failed invalid password",
            }
        )
    evs.append(
        {
            "id": "s0",
            "timestamp": base + timedelta(minutes=7),
            "actor": "alice",
            "event_type": "login",
            "severity": "info",
            "message": "login successful",
        }
    )
    return evs


def test_brute_force_detection():
    evs = make_events()
    dets = detections.detect_brute_force(evs, threshold=5, window_minutes=10)
    assert len(dets) >= 1
    d = dets[0]
    assert d["rule_id"] == "brute_force_auth"
    assert "alice" in d["description"]
    assert d["severity"] == "critical"
    assert "s0" in d["event_ids"]


def test_no_detection_below_threshold():
    evs = [
        {
            "id": "a",
            "timestamp": datetime(2024, 1, 1, tzinfo=UTC),
            "actor": "bob",
            "event_type": "login",
            "severity": "error",
            "message": "login failed",
        }
    ]
    dets = detections.detect_brute_force(evs, threshold=5, window_minutes=10)
    assert dets == []

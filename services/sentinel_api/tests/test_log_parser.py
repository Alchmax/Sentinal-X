from app.services import log_parser

CSV = "timestamp,actor,event_type,message\n2024-01-01T00:00:00Z,alice,login failed,invalid password\n2024-01-01T00:01:00Z,alice,login failed,bad creds\n"


def test_csv_parse():
    evs, _warnings, fmt = log_parser.parse_log(CSV, "a.csv")
    assert fmt == "csv"
    assert len(evs) == 2
    assert evs[0]["actor"] == "alice"
    assert evs[0]["timestamp"] is not None


def test_json_parse():
    import json

    content = json.dumps(
        {
            "events": [
                {
                    "timestamp": "2024-01-01T00:00:00Z",
                    "actor": "bob",
                    "event_type": "login",
                    "message": "ok",
                }
            ]
        }
    )
    evs, _warnings, fmt = log_parser.parse_log(content, "b.json")
    assert fmt == "json"
    assert len(evs) == 1


def test_timestamp_normalization():
    evs, warnings, fmt = (
        log_parser.parse_log("2024-01-01 12:00:00,alice,login,hi\n", "x.csv")
        if False
        else (None, None, None)
    )
    # csv needs header; use proper
    content = "timestamp,actor,event_type,message\n2024-01-01 12:00:00,alice,login,hi\n"
    evs, _warnings, _fmt = log_parser.parse_log(content, "x.csv")
    assert evs[0]["timestamp"].tzinfo is not None

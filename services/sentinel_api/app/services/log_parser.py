import csv
import json
import re
from datetime import UTC, datetime
from typing import Any


def _parse_ts(value: str) -> datetime | None:
    if not value:
        return None
    value = value.strip()
    formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(value, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=UTC)
            return dt
        except ValueError:
            continue
    # try ISO with offset
    try:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt
    except ValueError:
        return None


def parse_csv(content: str) -> tuple[list[dict[str, Any]], list[str]]:
    events = []
    warnings = []
    reader = csv.DictReader(content.splitlines())
    if not reader.fieldnames:
        return events, ["No header row found"]
    for i, row in enumerate(reader, start=2):
        try:
            ts_raw = (
                row.get("timestamp")
                or row.get("time")
                or row.get("date")
                or row.get("datetime")
                or ""
            )
            ts = _parse_ts(ts_raw)
            event = {
                "timestamp": ts,
                "source": row.get("source") or row.get("host") or "",
                "event_type": row.get("event_type")
                or row.get("type")
                or row.get("action")
                or "",
                "severity": row.get("severity") or row.get("level") or "",
                "actor": row.get("actor")
                or row.get("user")
                or row.get("username")
                or "",
                "target": row.get("target") or row.get("resource") or "",
                "message": row.get("message")
                or row.get("msg")
                or row.get("description")
                or "",
                "raw": ",".join(f"{k}={v}" for k, v in row.items()),
            }
            events.append(event)
        except Exception as e:
            warnings.append(f"Row {i}: {e}")
    return events, warnings


def parse_json(content: str) -> tuple[list[dict[str, Any]], list[str]]:
    events = []
    warnings = []
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        return events, [f"Invalid JSON: {e}"]
    if isinstance(data, dict):
        data = data.get("events") or data.get("records") or [data]
    if not isinstance(data, list):
        return events, ["JSON root is not a list"]
    for i, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            warnings.append(f"Item {i} is not an object")
            continue
        ts_raw = (
            item.get("timestamp")
            or item.get("time")
            or item.get("date")
            or item.get("datetime")
            or ""
        )
        ts = _parse_ts(str(ts_raw)) if ts_raw else None
        event = {
            "timestamp": ts,
            "source": item.get("source") or item.get("host") or "",
            "event_type": item.get("event_type")
            or item.get("type")
            or item.get("action")
            or "",
            "severity": item.get("severity") or item.get("level") or "",
            "actor": item.get("actor")
            or item.get("user")
            or item.get("username")
            or "",
            "target": item.get("target") or item.get("resource") or "",
            "message": item.get("message")
            or item.get("msg")
            or item.get("description")
            or "",
            "raw": json.dumps(item),
        }
        events.append(event)
    return events, warnings


def parse_text(content: str) -> tuple[list[dict[str, Any]], list[str]]:
    events = []
    warnings = []
    # common log line: timestamp level message
    ts_re = re.compile(r"^(\d{4}[-/]\d{2}[-/]\d{2}[ T]\d{2}:\d{2}:\d{2})")
    for i, line in enumerate(content.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        m = ts_re.match(line)
        if m:
            ts = _parse_ts(m.group(1))
            events.append(
                {
                    "timestamp": ts,
                    "source": "",
                    "event_type": "",
                    "severity": "",
                    "actor": "",
                    "target": "",
                    "message": line,
                    "raw": line,
                }
            )
        else:
            warnings.append(f"Line {i}: no timestamp detected")
    return events, warnings


def parse_log(
    content: str, filename: str = ""
) -> tuple[list[dict[str, Any]], list[str], str]:
    name = filename.lower()
    if name.endswith(".json"):
        ev, w = parse_json(content)
        return ev, w, "json"
    if name.endswith(".csv"):
        ev, w = parse_csv(content)
        return ev, w, "csv"
    # try json then csv
    try:
        json.loads(content)
        ev, w = parse_json(content)
        return ev, w, "json"
    except Exception:
        pass
    # if first line has commas and header-ish
    first = content.splitlines()[0] if content.splitlines() else ""
    if "," in first and ("timestamp" in first.lower() or "time" in first.lower()):
        ev, w = parse_csv(content)
        return ev, w, "csv"
    ev, w = parse_text(content)
    return ev, w, "text"

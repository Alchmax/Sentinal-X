from datetime import datetime as _dt
from datetime import timedelta
from typing import Any


def detect_brute_force(
    events: list[dict[str, Any]], threshold: int = 5, window_minutes: int = 10
) -> list[dict[str, Any]]:
    # events must have timestamp, actor, event_type/severity/message
    detections = []
    # group by actor
    by_actor: dict[str, list[dict[str, Any]]] = {}
    for e in events:
        actor = e.get("actor") or "unknown"
        by_actor.setdefault(actor, []).append(e)
    for actor, evs in by_actor.items():
        evs_sorted = sorted(evs, key=lambda x: x.get("timestamp") or datetime_min())
        # sliding window counting failed auth
        failed = [e for e in evs_sorted if _is_failed_auth(e)]
        for start_idx in range(len(failed)):
            window_start = failed[start_idx].get("timestamp")
            if window_start is None:
                continue
            window_end = window_start + timedelta(minutes=window_minutes)
            cluster = [
                e
                for e in failed
                if e.get("timestamp")
                and window_start <= e.get("timestamp") <= window_end
            ]
            if len(cluster) >= threshold:
                # check for success after cluster
                last_fail = max(
                    (e.get("timestamp") for e in cluster if e.get("timestamp")),
                    default=None,
                )
                success_after = None
                for e in evs_sorted:
                    if (
                        _is_success_auth(e)
                        and e.get("timestamp")
                        and last_fail
                        and e.get("timestamp") > last_fail
                    ):
                        success_after = e
                        break
                det = {
                    "rule_id": "brute_force_auth",
                    "title": "Repeated failed authentication attempts",
                    "description": f"{len(cluster)} failed authentication attempts for '{actor}' within {window_minutes} minutes.",
                    "severity": "high",
                    "event_ids": [str(e.get("id")) for e in cluster if e.get("id")],
                    "evidence": {
                        "actor": actor,
                        "count": len(cluster),
                        "window_minutes": window_minutes,
                    },
                }
                if success_after:
                    det["title"] = "Successful authentication after failed attempts"
                    det["description"] += (
                        " A successful authentication followed the cluster, suggesting possible credential compromise."
                    )
                    det["severity"] = "critical"
                    det["event_ids"] = det["event_ids"] + [str(success_after.get("id"))]
                    det["evidence"]["success_event_id"] = str(success_after.get("id"))
                detections.append(det)
                break
    return detections


def _is_failed_auth(e: dict[str, Any]) -> bool:
    et = (e.get("event_type") or "").lower()
    sev = (e.get("severity") or "").lower()
    msg = (e.get("message") or "").lower()
    if "fail" in et or "failed" in et:
        return True
    if "authentication" in et or "login" in et or "logon" in et:
        if (
            "fail" in msg
            or "invalid" in msg
            or "denied" in msg
            or sev in ("error", "warning", "high")
        ):
            # only count if failure indicators
            if "fail" in msg or "invalid" in msg or "denied" in msg:
                return True
    return bool("fail" in msg and ("auth" in msg or "login" in msg or "logon" in msg))


def _is_success_auth(e: dict[str, Any]) -> bool:
    et = (e.get("event_type") or "").lower()
    msg = (e.get("message") or "").lower()
    if "success" in et or "accepted" in et:
        return True
    if ("login" in et or "logon" in et or "auth" in et) and (
        "success" in msg or "accepted" in msg or "logged in" in msg
    ):
        return True
    return "successful" in msg




def datetime_min():
    return _dt.min.replace(tzinfo=_dt.timezone.utc)

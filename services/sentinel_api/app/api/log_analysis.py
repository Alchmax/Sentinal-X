import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.database import get_db
from ..models.evidence import AuditEvent, Finding, LogEvent
from ..models.user import User
from ..schemas.evidence import DetectionOut, LogEventOut, LogParseStats
from ..security.auth import get_current_user
from ..security.deps import require_case_owner
from ..services import detections, log_parser

router = APIRouter(prefix="/log-analysis", tags=["log-analysis"])


@router.post("/import", response_model=LogParseStats)
async def import_log(
    case_id: str = Form(...),
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_case_owner(db, case_id, user.id)
    content_bytes = await file.read(settings.max_upload_bytes + 1)
    if len(content_bytes) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="File too large")
    try:
        content = content_bytes.decode("utf-8", errors="replace")
    except Exception:
        content = content_bytes.decode("latin-1")
    evs, warnings, fmt = log_parser.parse_log(content, file.filename or "")
    saved = []
    for e in evs:
        le = LogEvent(
            id=str(uuid.uuid4()),
            case_id=case_id,
            timestamp=e.get("timestamp"),
            source=e.get("source", ""),
            event_type=e.get("event_type", ""),
            severity=e.get("severity", ""),
            actor=e.get("actor", ""),
            target=e.get("target", ""),
            message=e.get("message", ""),
            raw=e.get("raw", ""),
            parser_warnings=e.get("parser_warnings", []),
        )
        db.add(le)
        saved.append(le)
    db.add(
        AuditEvent(
            case_id=case_id,
            actor_id=user.id,
            action="log_imported",
            target_type="case",
            target_id=case_id,
            details={
                "format": fmt,
                "parsed": len(saved),
                "skipped_warnings": len(warnings),
            },
        )
    )
    db.commit()
    out_events = [
        LogEventOut(
            id=e.id,
            case_id=e.case_id,
            timestamp=e.timestamp,
            source=e.source,
            event_type=e.event_type,
            severity=e.severity,
            actor=e.actor,
            target=e.target,
            message=e.message,
            created_at=e.created_at,
        )
        for e in saved
    ]
    return LogParseStats(
        total_lines=content.count("\n") + 1,
        parsed=len(saved),
        skipped=len(warnings),
        warnings=warnings,
        events=out_events,
    )


@router.get("/events/{case_id}", response_model=list[LogEventOut])
def list_events(
    case_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    require_case_owner(db, case_id, user.id)
    items = (
        db.query(LogEvent)
        .filter(LogEvent.case_id == case_id)
        .order_by(LogEvent.timestamp)
        .all()
    )
    return [
        LogEventOut(
            id=e.id,
            case_id=e.case_id,
            timestamp=e.timestamp,
            source=e.source,
            event_type=e.event_type,
            severity=e.severity,
            actor=e.actor,
            target=e.target,
            message=e.message,
            created_at=e.created_at,
        )
        for e in items
    ]


@router.post("/detect/{case_id}", response_model=list[DetectionOut])
def run_detections(
    case_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    require_case_owner(db, case_id, user.id)
    items = db.query(LogEvent).filter(LogEvent.case_id == case_id).all()
    ev_dicts = [
        {
            "id": e.id,
            "timestamp": e.timestamp,
            "actor": e.actor,
            "event_type": e.event_type,
            "severity": e.severity,
            "message": e.message,
            "target": e.target,
        }
        for e in items
    ]
    dets = detections.detect_brute_force(ev_dicts)
    # save as findings
    for d in dets:
        f = Finding(
            case_id=case_id,
            kind="detection",
            title=d["title"],
            description=d["description"],
            evidence_refs=d["event_ids"],
            confidence="high",
        )
        db.add(f)
    db.add(
        AuditEvent(
            case_id=case_id,
            actor_id=user.id,
            action="detections_run",
            target_type="case",
            target_id=case_id,
            details={"count": len(dets)},
        )
    )
    db.commit()
    return [
        DetectionOut(
            rule_id=d["rule_id"],
            title=d["title"],
            description=d["description"],
            severity=d["severity"],
            event_ids=d["event_ids"],
            evidence=d["evidence"],
        )
        for d in dets
    ]

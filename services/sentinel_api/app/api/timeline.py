import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..security.auth import get_current_user
from ..security.deps import require_case_owner
from ..models.user import User
from ..models.evidence import TimelineEntry, LogEvent, Evidence, Finding, AuditEvent
from ..schemas.evidence import TimelineEntryOut

router = APIRouter(prefix="/timeline", tags=["timeline"])

@router.post("/build/{case_id}")
def build_timeline(case_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_case_owner(db, case_id, user.id)
    # clear existing
    db.query(TimelineEntry).filter(TimelineEntry.case_id == case_id).delete()
    # from evidence
    for e in db.query(Evidence).filter(Evidence.case_id == case_id).all():
        db.add(TimelineEntry(case_id=case_id, timestamp=e.created_at, entry_type="evidence", title=f"Evidence: {e.filename}", description=f"SHA-256 {e.sha256}", refs=[e.id]))
    # from log events
    for ev in db.query(LogEvent).filter(LogEvent.case_id == case_id).all():
        db.add(TimelineEntry(case_id=case_id, timestamp=ev.timestamp, entry_type="log_event", title=ev.event_type or "Log event", description=ev.message, refs=[ev.id]))
    # from findings
    for f in db.query(Finding).filter(Finding.case_id == case_id).all():
        db.add(TimelineEntry(case_id=case_id, timestamp=f.created_at, entry_type="finding", title=f.title, description=f.description, refs=[f.id] + (f.evidence_refs or [])))
    db.add(AuditEvent(case_id=case_id, actor_id=user.id, action="timeline_built", target_type="case", target_id=case_id))
    db.commit()
    return {"built": True}

@router.get("/{case_id}", response_model=list[TimelineEntryOut])
def get_timeline(case_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_case_owner(db, case_id, user.id)
    items = db.query(TimelineEntry).filter(TimelineEntry.case_id == case_id).order_by(TimelineEntry.timestamp).all()
    return [TimelineEntryOut(id=t.id, case_id=t.case_id, timestamp=t.timestamp, entry_type=t.entry_type, title=t.title, description=t.description, refs=t.refs or []) for t in items]
import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.case import Case
from ..models.evidence import (
    AuditEvent,
    CaseNote,
    Evidence,
    Finding,
    LogEvent,
    Report,
    TimelineEntry,
)
from ..models.user import User
from ..schemas.evidence import ReportOut
from ..security.auth import get_current_user
from ..security.deps import require_case_owner
from ..services import report_service

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/generate/{case_id}", response_model=ReportOut)
def generate_report(
    case_id: str,
    format: str = "html",
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_case_owner(db, case_id, user.id)
    case = db.query(Case).filter(Case.id == case_id).first()
    evidence_list = db.query(Evidence).filter(Evidence.case_id == case_id).all()
    findings = db.query(Finding).filter(Finding.case_id == case_id).all()
    events = db.query(LogEvent).filter(LogEvent.case_id == case_id).all()
    timeline = db.query(TimelineEntry).filter(TimelineEntry.case_id == case_id).all()
    notes = db.query(CaseNote).filter(CaseNote.case_id == case_id).all()
    content = report_service.generate_html_report(
        case, evidence_list, findings, events, timeline, notes, []
    )
    r = Report(
        id=str(uuid.uuid4()),
        case_id=case_id,
        format=format,
        title="Report for %s" % case.title,
        content=content,
    )
    db.add(r)
    db.add(
        AuditEvent(
            case_id=case_id,
            actor_id=user.id,
            action="report_generated",
            target_type="report",
            target_id=r.id,
            details={"format": format},
        )
    )
    db.commit()
    db.refresh(r)
    return ReportOut(
        id=r.id,
        case_id=r.case_id,
        format=r.format,
        title=r.title,
        content=r.content,
        created_at=r.created_at,
    )


@router.get("/pdf/{case_id}")
def generate_pdf(
    case_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_case_owner(db, case_id, user.id)
    case = db.query(Case).filter(Case.id == case_id).first()
    evidence_list = db.query(Evidence).filter(Evidence.case_id == case_id).all()
    findings = db.query(Finding).filter(Finding.case_id == case_id).all()
    events = db.query(LogEvent).filter(LogEvent.case_id == case_id).all()
    timeline = db.query(TimelineEntry).filter(TimelineEntry.case_id == case_id).all()
    notes = db.query(CaseNote).filter(CaseNote.case_id == case_id).all()
    pdf_bytes = report_service.generate_pdf_report(
        case, evidence_list, findings, events, timeline, notes
    )
    if not pdf_bytes:
        from fastapi import HTTPException

        raise HTTPException(status_code=500, detail="PDF generation unavailable")
    db.add(
        AuditEvent(
            case_id=case_id,
            actor_id=user.id,
            action="report_generated",
            target_type="report",
            target_id=case_id,
            details={"format": "pdf"},
        )
    )
    db.commit()
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=report-%s.pdf" % case_id},
    )


@router.get("/{report_id}", response_model=ReportOut)
def get_report(
    report_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    r = db.query(Report).filter(Report.id == report_id).first()
    if not r:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Report not found")
    require_case_owner(db, r.case_id, user.id)
    return ReportOut(
        id=r.id,
        case_id=r.case_id,
        format=r.format,
        title=r.title,
        content=r.content,
        created_at=r.created_at,
    )


@router.get("/case/{case_id}", response_model=list[ReportOut])
def list_reports(
    case_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_case_owner(db, case_id, user.id)
    items = db.query(Report).filter(Report.case_id == case_id).order_by(
        Report.created_at.desc()
    ).all()
    return [
        ReportOut(
            id=r.id,
            case_id=r.case_id,
            format=r.format,
            title=r.title,
            content=r.content,
            created_at=r.created_at,
        )
        for r in items
    ]
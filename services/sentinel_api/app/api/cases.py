from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.case import Case
from ..models.evidence import AuditEvent, CaseNote, Finding
from ..models.user import User
from ..schemas.case import (
    CaseCreate,
    CaseNoteCreate,
    CaseNoteOut,
    CaseOut,
    CaseUpdate,
    FindingCreate,
    FindingOut,
)
from ..security.auth import get_current_user
from ..security.deps import require_case_owner
from ..services import case_service

router = APIRouter(prefix="/cases", tags=["cases"])


def _case_out(c: Case) -> CaseOut:
    return CaseOut(
        id=c.id,
        title=c.title,
        description=c.description,
        status=c.status,
        priority=c.priority,
        tags=c.tags_list(),
        owner_id=c.owner_id,
        created_at=c.created_at,
        updated_at=c.updated_at,
        archived_at=c.archived_at,
    )


@router.post("", response_model=CaseOut)
def create_case(
    data: CaseCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    c = case_service.create_case(db, user.id, data)
    db.add(
        AuditEvent(
            case_id=c.id,
            actor_id=user.id,
            action="case_created",
            target_type="case",
            target_id=c.id,
        )
    )
    db.commit()
    return _case_out(c)


@router.get("", response_model=dict)
def list_cases(
    q: str = "",
    status: str = "",
    limit: int = 50,
    offset: int = 0,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items, total = case_service.list_cases(db, user.id, q, status, limit, offset)
    return {"items": [_case_out(c) for c in items], "total": total}


@router.get("/{case_id}", response_model=CaseOut)
def get_case(
    case_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    case = require_case_owner(db, case_id, user.id)
    return _case_out(case)


@router.patch("/{case_id}", response_model=CaseOut)
def update_case(
    case_id: str,
    data: CaseUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    case = require_case_owner(db, case_id, user.id)
    c = case_service.update_case(db, case, data)
    db.add(
        AuditEvent(
            case_id=c.id,
            actor_id=user.id,
            action="case_updated",
            target_type="case",
            target_id=c.id,
        )
    )
    db.commit()
    return _case_out(c)


@router.post("/{case_id}/archive", response_model=CaseOut)
def archive_case(
    case_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    case = require_case_owner(db, case_id, user.id)
    c = case_service.archive_case(db, case)
    db.add(
        AuditEvent(
            case_id=c.id,
            actor_id=user.id,
            action="case_archived",
            target_type="case",
            target_id=c.id,
        )
    )
    db.commit()
    return _case_out(c)


@router.delete("/{case_id}")
def delete_case(
    case_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    case = require_case_owner(db, case_id, user.id)
    case_service.delete_case(db, case)
    return {"deleted": True}


# notes
@router.post("/{case_id}/notes", response_model=CaseNoteOut)
def add_note(
    case_id: str,
    data: CaseNoteCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_case_owner(db, case_id, user.id)
    note = CaseNote(case_id=case_id, author_id=user.id, content=data.content)
    db.add(note)
    db.add(
        AuditEvent(
            case_id=case_id,
            actor_id=user.id,
            action="note_added",
            target_type="note",
            target_id=note.id,
        )
    )
    db.commit()
    db.refresh(note)
    return CaseNoteOut(
        id=note.id,
        case_id=note.case_id,
        content=note.content,
        created_at=note.created_at,
    )


@router.get("/{case_id}/notes", response_model=list[CaseNoteOut])
def list_notes(
    case_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    require_case_owner(db, case_id, user.id)
    notes = (
        db.query(CaseNote)
        .filter(CaseNote.case_id == case_id)
        .order_by(CaseNote.created_at.desc())
        .all()
    )
    return [
        CaseNoteOut(
            id=n.id, case_id=n.case_id, content=n.content, created_at=n.created_at
        )
        for n in notes
    ]


# findings
@router.post("/{case_id}/findings", response_model=FindingOut)
def add_finding(
    case_id: str,
    data: FindingCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_case_owner(db, case_id, user.id)
    f = Finding(
        case_id=case_id,
        kind=data.kind,
        title=data.title,
        description=data.description,
        evidence_refs=data.evidence_refs,
        confidence=data.confidence,
    )
    db.add(f)
    db.add(
        AuditEvent(
            case_id=case_id,
            actor_id=user.id,
            action="finding_added",
            target_type="finding",
            target_id=f.id,
        )
    )
    db.commit()
    db.refresh(f)
    return FindingOut(
        id=f.id,
        case_id=f.case_id,
        kind=f.kind,
        title=f.title,
        description=f.description,
        evidence_refs=f.evidence_refs or [],
        confidence=f.confidence,
        created_at=f.created_at,
    )


@router.get("/{case_id}/findings", response_model=list[FindingOut])
def list_findings(
    case_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    require_case_owner(db, case_id, user.id)
    fs = (
        db.query(Finding)
        .filter(Finding.case_id == case_id)
        .order_by(Finding.created_at.desc())
        .all()
    )
    return [
        FindingOut(
            id=f.id,
            case_id=f.case_id,
            kind=f.kind,
            title=f.title,
            description=f.description,
            evidence_refs=f.evidence_refs or [],
            confidence=f.confidence,
            created_at=f.created_at,
        )
        for f in fs
    ]

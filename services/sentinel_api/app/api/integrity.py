import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.evidence import AuditEvent, IntegrityBaseline
from ..models.user import User
from ..security.auth import get_current_user
from ..services import integrity as integrity_service

router = APIRouter(prefix="/integrity", tags=["integrity"])


class BaselineRequest(BaseModel):
    case_id: str | None = None
    root_path: str


class RescanRequest(BaseModel):
    baseline_id: str


@router.post("/baseline")
def create_baseline(
    data: BaselineRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if data.case_id:
        from ..security.deps import require_case_owner

        require_case_owner(db, data.case_id, user.id)
    # path traversal defense: resolve
    import os

    root = os.path.abspath(data.root_path)
    if not os.path.isdir(root):
        raise HTTPException(status_code=400, detail="Directory not found")
    entries = integrity_service.build_baseline(root)
    b = IntegrityBaseline(
        id=str(uuid.uuid4()), case_id=data.case_id, root_path=root, entries=entries
    )
    db.add(b)
    db.add(
        AuditEvent(
            case_id=data.case_id,
            actor_id=user.id,
            action="integrity_baseline_created",
            target_type="integrity_baseline",
            target_id=b.id,
            details={"root": root, "count": len(entries)},
        )
    )
    db.commit()
    db.refresh(b)
    return {
        "id": b.id,
        "root_path": b.root_path,
        "entry_count": len(entries),
        "created_at": b.created_at,
    }


@router.post("/rescan")
def rescan(
    data: RescanRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    b = (
        db.query(IntegrityBaseline)
        .filter(IntegrityBaseline.id == data.baseline_id)
        .first()
    )
    if not b:
        raise HTTPException(status_code=404, detail="Baseline not found")
    if b.case_id:
        from ..security.deps import require_case_owner

        require_case_owner(db, b.case_id, user.id)
    diff = integrity_service.compare_baseline(b.entries or [], b.root_path)
    db.add(
        AuditEvent(
            case_id=b.case_id,
            actor_id=user.id,
            action="integrity_rescan",
            target_type="integrity_baseline",
            target_id=b.id,
            details={
                "added": len(diff["added"]),
                "deleted": len(diff["deleted"]),
                "modified": len(diff["modified"]),
            },
        )
    )
    db.commit()
    return {"baseline_id": b.id, "root_path": b.root_path, **diff}


@router.get("/baselines/{case_id}")
def list_baselines(
    case_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    from ..security.deps import require_case_owner

    require_case_owner(db, case_id, user.id)
    items = (
        db.query(IntegrityBaseline).filter(IntegrityBaseline.case_id == case_id).all()
    )
    return [
        {
            "id": b.id,
            "root_path": b.root_path,
            "entry_count": len(b.entries or []),
            "created_at": b.created_at,
        }
        for b in items
    ]

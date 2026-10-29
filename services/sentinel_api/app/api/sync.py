import uuid
from datetime import UTC

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.evidence import SyncRecord
from ..models.user import User
from ..security.auth import get_current_user

router = APIRouter(prefix="/sync", tags=["sync"])


class SyncRequest(BaseModel):
    entity_type: str
    entity_id: str
    version: str = "1"


@router.post("/enqueue")
def enqueue(
    data: SyncRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rec = SyncRecord(
        id=str(uuid.uuid4()),
        entity_type=data.entity_type,
        entity_id=data.entity_id,
        version=data.version,
        status="pending",
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return {"id": rec.id, "status": rec.status}


@router.post("/complete/{record_id}")
def complete(
    record_id: str,
    status: str = "completed",
    error: str = "",
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rec = db.query(SyncRecord).filter(SyncRecord.id == record_id).first()
    if not rec:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Record not found")
    from datetime import datetime

    rec.status = status
    rec.error = error
    if status == "completed":
        rec.last_synced_at = datetime.now(UTC)
    db.commit()
    db.refresh(rec)
    return {"id": rec.id, "status": rec.status}


@router.get("/status", response_model=list[dict])
def status_list(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.query(SyncRecord).order_by(SyncRecord.created_at.desc()).limit(100).all()
    return [
        {
            "id": r.id,
            "entity_type": r.entity_type,
            "entity_id": r.entity_id,
            "status": r.status,
            "last_synced_at": r.last_synced_at,
            "error": r.error,
        }
        for r in items
    ]

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.case import Case
from app.security.auth import get_current_user
from app.models.user import User
import uuid
import os
from datetime import datetime

router = APIRouter()

@router.post("/full-scan")
async def run_full_scan(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Simulates a full device forensic scan.
    Creates a new case and runs an integrity baseline scan.
    Returns the case ID and entry count.
    """
    try:
        from app.services import integrity as integrity_service
        from app.models.evidence import IntegrityBaseline, AuditEvent
        
        system_user_id = user.id 
        
        # 1. Create a new case for the scan
        new_case = Case(
            id=f"case_{uuid.uuid4().hex[:8]}",
            title="Global Device Scan",
            description="Automatically generated case from full device forensic scan.",
            status="open",
            priority="high",
            tags="full-scan, automated",
            owner_id=system_user_id
        )
        db.add(new_case)
        db.commit()
        db.refresh(new_case)
        
        # 2. Run integrity baseline scan (same as Device Scan in Cases section)
        root_path = "C:/Users"
        root = os.path.abspath(root_path)
        entry_count = 0
        if os.path.isdir(root):
            entries = integrity_service.build_baseline(root, max_files=200)
            b = IntegrityBaseline(
                id=str(uuid.uuid4()), case_id=new_case.id, root_path=root, entries=entries
            )
            db.add(b)
            db.add(
                AuditEvent(
                    case_id=new_case.id,
                    actor_id=system_user_id,
                    action="integrity_baseline_created",
                    target_type="integrity_baseline",
                    target_id=b.id,
                    details={"root": root, "count": len(entries)},
                )
            )
            db.commit()
            entry_count = len(entries)
        
        return {"case_id": new_case.id, "status": "Scan initiated", "entry_count": entry_count}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
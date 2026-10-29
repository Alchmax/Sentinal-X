from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..core.database import get_db
from ..security.auth import get_current_user
from ..security.deps import require_case_owner
from ..models.user import User
from ..schemas.evidence import EvidenceOut, FileAnalysisResult
from ..services import evidence_service, file_forensics

router = APIRouter(prefix="/evidence", tags=["evidence"])

@router.post("/analyze", response_model=FileAnalysisResult)
async def analyze_file(file: UploadFile = File(...)):
    import tempfile
    import os
    suffix = os.path.splitext(file.filename or "")[1]
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    try:
        return file_forensics.analyze_file(tmp_path)
    finally:
        os.remove(tmp_path)

@router.post("/register", response_model=EvidenceOut)
async def register_evidence(
    case_id: str = Form(...),
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_case_owner(db, case_id, user.id)
    content = await file.read()
    return await evidence_service.register_evidence(
        db, case_id, user.id, content, file.filename, file.content_type
    )

@router.get("/case/{case_id}", response_model=List[EvidenceOut])
async def list_evidence(case_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_case_owner(db, case_id, user.id)
    return await evidence_service.get_evidence_by_case(db, case_id)
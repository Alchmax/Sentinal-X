from sqlalchemy.orm import Session
from ..models.evidence import Evidence, AuditEvent
from ..schemas.evidence import EvidenceOut, FileAnalysisResult
from ..services import file_forensics
import uuid
import os
import tempfile

async def register_evidence(db: Session, case_id: str, user_id: str, file_content: bytes, filename: str, content_type: str) -> EvidenceOut:
    # Save to temp file for analysis
    suffix = os.path.splitext(filename or "")[1]
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(file_content)
        tmp_path = tmp.name
    
    try:
        # Perform forensic analysis
        analysis = file_forensics.analyze_file(tmp_path)
        
        ev = Evidence(
            id=str(uuid.uuid4()),
            case_id=case_id,
            filename=filename,
            size_bytes=analysis["size_bytes"],
            sha256=analysis["sha256"],
            content_type=analysis["mime_guess"],
            extension=analysis["extension"],
            detected_signature=analysis["detected_signature"],
            metadata_json=analysis["metadata"],
            source_path=tmp_path
        )
        db.add(ev)
        db.add(AuditEvent(
            case_id=case_id, 
            actor_id=user_id, 
            action="evidence_registered", 
            target_type="evidence", 
            target_id=ev.id, 
            details={"sha256": ev.sha256}
        ))
        db.commit()
        db.refresh(ev)
        return EvidenceOut.model_validate(ev)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

async def get_evidence_by_case(db: Session, case_id: str) -> list[EvidenceOut]:
    items = db.query(Evidence).filter(Evidence.case_id == case_id).all()
    return [EvidenceOut.model_validate(e) for e in items]
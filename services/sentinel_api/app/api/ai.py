from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..ai.context_builder import build_context, validate_citations
from ..ai.ollama_client import OllamaClient, OllamaError
from ..core.config import settings
from ..core.database import get_db
from ..models.evidence import CaseNote, Evidence, Finding, LogEvent
from ..models.user import User
from ..schemas.ai import AIChatRequest, AIChatResponse, AIContextPreview, AIStatus
from ..security.auth import get_current_user
from ..security.deps import require_case_owner

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/status", response_model=AIStatus)
def ai_status():
    client = OllamaClient()
    configured = client.is_configured() and settings.ai_enabled
    reason = ""
    if not settings.ai_enabled:
        reason = "AI disabled by configuration"
    elif not settings.ollama_api_key:
        reason = "Missing OLLAMA_API_KEY"
    elif not settings.ollama_model:
        reason = "Missing OLLAMA_MODEL"
    return AIStatus(
        enabled=settings.ai_enabled,
        configured=configured,
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        reason=reason,
    )


@router.post("/preview", response_model=AIContextPreview)
def preview_context(
    data: AIChatRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if data.case_id:
        require_case_owner(db, data.case_id, user.id)
    records = _gather_records(db, data)
    ctx = build_context(data.question, records, settings.ai_max_context_chars)
    return AIContextPreview(
        summary=ctx[:500], char_count=len(ctx), records=records, will_leave_device=True
    )


@router.post("/chat", response_model=AIChatResponse)
async def chat(
    data: AIChatRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not data.approved:
        return AIChatResponse(
            answer="", error="Context must be approved before transmission"
        )
    if not settings.ai_enabled:
        return AIChatResponse(answer="", error="AI is disabled")
    client = OllamaClient()
    if not client.is_configured():
        return AIChatResponse(answer="", error="AI not configured")
    if data.case_id:
        require_case_owner(db, data.case_id, user.id)
    records = _gather_records(db, data)
    supplied_ids = [r["id"] for r in records]
    ctx = build_context(data.question, records, settings.ai_max_context_chars)
    messages = [{"role": "user", "content": ctx}]
    try:
        answer = await client.chat(messages)
    except OllamaError as e:
        return AIChatResponse(answer="", error=str(e))
    valid, invalid = validate_citations(answer, supplied_ids)
    # audit
    from ..models.evidence import AuditEvent

    db.add(
        AuditEvent(
            case_id=data.case_id,
            actor_id=user.id,
            action="ai_chat",
            target_type="case",
            target_id=data.case_id or "",
            details={"context_chars": len(ctx), "model": settings.ollama_model},
        )
    )
    db.commit()
    return AIChatResponse(
        answer=answer,
        citations=valid,
        invalid_citations=invalid,
        model=settings.ollama_model,
    )


def _gather_records(db, data: AIChatRequest) -> list[dict]:
    records = []
    if data.case_id:
        # evidence
        for e in (
            db.query(Evidence).filter(Evidence.case_id == data.case_id).limit(20).all()
        ):
            records.append(
                {
                    "id": e.id,
                    "type": "evidence",
                    "content": f"{e.filename} sha256={e.sha256} size={e.size_bytes} sig={e.detected_signature}",
                }
            )
        # findings
        for f in (
            db.query(Finding).filter(Finding.case_id == data.case_id).limit(20).all()
        ):
            records.append(
                {
                    "id": f.id,
                    "type": "finding",
                    "content": f"{f.kind}: {f.title} - {f.description}",
                }
            )
        # recent events
        for ev in (
            db.query(LogEvent)
            .filter(LogEvent.case_id == data.case_id)
            .order_by(LogEvent.timestamp.desc())
            .limit(30)
            .all()
        ):
            records.append(
                {
                    "id": ev.id,
                    "type": "log_event",
                    "content": f"{ev.timestamp} {ev.actor} {ev.event_type} {ev.message}",
                }
            )
        # notes
        for n in (
            db.query(CaseNote).filter(CaseNote.case_id == data.case_id).limit(10).all()
        ):
            records.append({"id": n.id, "type": "note", "content": n.content})
    # selected context ids filter
    if data.context_ids:
        allowed = set(data.context_ids)
        records = [r for r in records if r["id"] in allowed]
    return records

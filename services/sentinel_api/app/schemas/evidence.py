from datetime import datetime
from typing import Any

from pydantic import BaseModel


class EvidenceOut(BaseModel):
    id: str
    case_id: str
    filename: str
    size_bytes: int
    sha256: str | None = None
    content_type: str = ""
    extension: str = ""
    detected_signature: str = ""
    metadata: dict = {}
    source_path: str = ""
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class FileAnalysisResult(BaseModel):
    filename: str
    size_bytes: int
    sha256: str
    extension: str
    detected_signature: str
    mime_guess: str = ""
    mismatch: bool = False
    mismatch_reason: str = ""
    metadata: dict = {}
    warnings: list[str] = []


class LogEventOut(BaseModel):
    id: str
    case_id: str
    timestamp: datetime | None = None
    source: str = ""
    event_type: str = ""
    severity: str = ""
    actor: str = ""
    target: str = ""
    message: str = ""
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class LogParseStats(BaseModel):
    total_lines: int = 0
    parsed: int = 0
    skipped: int = 0
    warnings: list[str] = []
    events: list[LogEventOut] = []


class DetectionOut(BaseModel):
    rule_id: str
    title: str
    description: str
    severity: str = "medium"
    event_ids: list[str] = []
    evidence: dict = {}


class TimelineEntryOut(BaseModel):
    id: str
    case_id: str
    timestamp: datetime | None = None
    entry_type: str = ""
    title: str = ""
    description: str = ""
    refs: list[Any] = []

    class Config:
        from_attributes = True


class IntegrityEntry(BaseModel):
    path: str
    size: int
    mtime: float
    sha256: str


class IntegrityDiff(BaseModel):
    added: list[str] = []
    deleted: list[str] = []
    modified: list[dict] = []
    unchanged: int = 0


class ReportOut(BaseModel):
    id: str
    case_id: str
    format: str
    title: str
    content: str
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class SyncStatus(BaseModel):
    entity_type: str
    entity_id: str
    status: str
    last_synced_at: datetime | None = None
    error: str = ""


class AuditEventOut(BaseModel):
    id: str
    case_id: str | None = None
    action: str
    target_type: str = ""
    target_id: str = ""
    details: dict = {}
    created_at: datetime | None = None

    class Config:
        from_attributes = True

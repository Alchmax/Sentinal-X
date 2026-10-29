import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, BigInteger, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from ..core.database import Base


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String, ForeignKey("cases.id"), nullable=False, index=True)
    filename = Column(String, nullable=False)
    size_bytes = Column(BigInteger, default=0)
    sha256 = Column(String, nullable=True, index=True)
    content_type = Column(String, default="")
    extension = Column(String, default="")
    detected_signature = Column(String, default="")
    metadata_json = Column(JSON, default=dict)
    source_path = Column(String, default="")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    case = relationship("Case", back_populates="evidence")


class CaseNote(Base):
    __tablename__ = "case_notes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String, ForeignKey("cases.id"), nullable=False, index=True)
    author_id = Column(String, ForeignKey("users.id"), nullable=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    case = relationship("Case", back_populates="notes")


class Finding(Base):
    __tablename__ = "findings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String, ForeignKey("cases.id"), nullable=False, index=True)
    kind = Column(String, default="observation")  # observation|detection|hypothesis
    title = Column(String, nullable=False)
    description = Column(Text, default="")
    evidence_refs = Column(JSON, default=list)
    confidence = Column(String, default="unknown")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    case = relationship("Case", back_populates="findings")


class LogEvent(Base):
    __tablename__ = "log_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String, ForeignKey("cases.id"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=True, index=True)
    source = Column(String, default="")
    event_type = Column(String, default="")
    severity = Column(String, default="")
    actor = Column(String, default="")
    target = Column(String, default="")
    message = Column(Text, default="")
    raw = Column(Text, default="")
    parser_warnings = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    case = relationship("Case", back_populates="events")


class TimelineEntry(Base):
    __tablename__ = "timeline_entries"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String, ForeignKey("cases.id"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=True, index=True)
    entry_type = Column(String, default="")
    title = Column(String, default="")
    description = Column(Text, default="")
    refs = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    case = relationship("Case", back_populates="timeline_entries")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String, ForeignKey("cases.id"), nullable=True, index=True)
    actor_id = Column(String, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    target_type = Column(String, default="")
    target_id = Column(String, default="")
    details = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    case = relationship("Case", back_populates="audit_events")


class IntegrityBaseline(Base):
    __tablename__ = "integrity_baselines"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String, ForeignKey("cases.id"), nullable=True, index=True)
    root_path = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    entries = Column(JSON, default=list)  # list of {path, size, mtime, sha256}


class SyncRecord(Base):
    __tablename__ = "sync_records"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_type = Column(String, nullable=False)
    entity_id = Column(String, nullable=False, index=True)
    version = Column(String, default="1")
    status = Column(String, default="pending")  # pending|completed|failed|conflict
    last_synced_at = Column(DateTime(timezone=True), nullable=True)
    error = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String, ForeignKey("cases.id"), nullable=False, index=True)
    format = Column(String, default="html")
    title = Column(String, default="")
    content = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

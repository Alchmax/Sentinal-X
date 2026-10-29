import enum
import uuid
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from ..core.database import Base


class CaseStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    closed = "closed"
    archived = "archived"


class CasePriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Case(Base):
    __tablename__ = "cases"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(Text, default="")
    status = Column(String, default=CaseStatus.open.value)
    priority = Column(String, default=CasePriority.medium.value)
    tags = Column(String, default="")
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    archived_at = Column(DateTime(timezone=True), nullable=True)

    owner = relationship("User", back_populates="cases")
    evidence = relationship(
        "Evidence", back_populates="case", cascade="all, delete-orphan"
    )
    notes = relationship(
        "CaseNote", back_populates="case", cascade="all, delete-orphan"
    )
    findings = relationship(
        "Finding", back_populates="case", cascade="all, delete-orphan"
    )
    events = relationship(
        "LogEvent", back_populates="case", cascade="all, delete-orphan"
    )
    timeline_entries = relationship(
        "TimelineEntry", back_populates="case", cascade="all, delete-orphan"
    )
    audit_events = relationship(
        "AuditEvent", back_populates="case", cascade="all, delete-orphan"
    )

    def tags_list(self):
        return (
            [t.strip() for t in self.tags.split(",") if t.strip()] if self.tags else []
        )

from datetime import datetime

from pydantic import BaseModel, Field


class CaseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = ""
    status: str = "open"
    priority: str = "medium"
    tags: list[str] = []


class CaseUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    tags: list[str] | None = None


class CaseOut(BaseModel):
    id: str
    title: str
    description: str
    status: str
    priority: str
    tags: list[str] = []
    owner_id: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    archived_at: datetime | None = None

    class Config:
        from_attributes = True


class CaseNoteCreate(BaseModel):
    content: str = Field(min_length=1)


class CaseNoteOut(BaseModel):
    id: str
    case_id: str
    content: str
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class FindingCreate(BaseModel):
    kind: str = "observation"
    title: str
    description: str = ""
    evidence_refs: list[str] = []
    confidence: str = "unknown"


class FindingOut(BaseModel):
    id: str
    case_id: str
    kind: str
    title: str
    description: str
    evidence_refs: list[str] = []
    confidence: str
    created_at: datetime | None = None

    class Config:
        from_attributes = True

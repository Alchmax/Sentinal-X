from pydantic import BaseModel


class AIStatus(BaseModel):
    enabled: bool
    configured: bool
    model: str = ""
    base_url: str = ""
    reason: str = ""


class AIChatRequest(BaseModel):
    case_id: str | None = None
    question: str
    context_ids: list[str] = []
    approved: bool = False
    preview_only: bool = False


class AIContextPreview(BaseModel):
    summary: str
    char_count: int
    records: list[dict] = []
    will_leave_device: bool = True
    provider: str = "Ollama Cloud"


class AIChatResponse(BaseModel):
    answer: str
    citations: list[str] = []
    invalid_citations: list[str] = []
    model: str = ""
    provider: str = "Ollama Cloud"
    error: str | None = None

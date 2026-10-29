from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "Sentinel X API"
    app_version: str = "0.1.0"
    debug: bool = False

    database_url: str = (
        "postgresql+psycopg2://sentinel:sentinel@localhost:5432/sentinel"
    )

    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    cors_origins: str = "http://localhost:3000,http://localhost:8080"

    # Ollama Cloud
    ollama_api_key: str = Field(default="", alias="OLLAMA_API_KEY")
    ollama_base_url: str = Field(
        default="https://api.ollama.com", alias="OLLAMA_BASE_URL"
    )
    ollama_model: str = Field(default="", alias="OLLAMA_MODEL")
    ai_enabled: bool = Field(default=False, alias="AI_ENABLED")
    ai_request_timeout_seconds: int = Field(
        default=60, alias="AI_REQUEST_TIMEOUT_SECONDS"
    )
    ai_max_context_chars: int = Field(default=24000, alias="AI_MAX_CONTEXT_CHARS")
    ai_allow_evidence_upload: bool = Field(
        default=False, alias="AI_ALLOW_EVIDENCE_UPLOAD"
    )

    max_upload_bytes: int = 50 * 1024 * 1024
    local_agent_token: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def ai_configured(self) -> bool:
        return bool(self.ollama_api_key) and bool(self.ollama_model) and self.ai_enabled


settings = Settings()

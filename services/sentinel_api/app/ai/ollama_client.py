import httpx

from ..core.config import settings


class OllamaError(Exception):
    pass


class OllamaAuthError(OllamaError):
    pass


class OllamaRateLimitError(OllamaError):
    pass


class OllamaModelError(OllamaError):
    pass


class OllamaNetworkError(OllamaError):
    pass


class OllamaMalformedError(OllamaError):
    pass


class OllamaClient:
    def __init__(
        self, base_url: str = "", api_key: str = "", model: str = "", timeout: int = 60
    ):
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.api_key = api_key or settings.ollama_api_key
        self.model = model or settings.ollama_model
        self.timeout = timeout or settings.ai_request_timeout_seconds

    def is_configured(self) -> bool:
        return bool(self.api_key) and bool(self.model)

    def _headers(self) -> dict:
        h = {"Content-Type": "application/json"}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    async def chat(self, messages: list[dict], timeout: int | None = None) -> str:
        if not self.is_configured():
            raise OllamaAuthError("Ollama not configured")
        t = timeout or self.timeout
        url = f"{self.base_url}/api/chat"
        payload = {"model": self.model, "messages": messages, "stream": False}
        try:
            async with httpx.AsyncClient(timeout=t) as client:
                resp = await client.post(url, json=payload, headers=self._headers())
        except httpx.TimeoutException as e:
            raise OllamaNetworkError(f"Timeout: {e}")
        except httpx.RequestError as e:
            raise OllamaNetworkError(str(e))
        if resp.status_code == 401 or resp.status_code == 403:
            raise OllamaAuthError("Authentication failed")
        if resp.status_code == 429:
            raise OllamaRateLimitError("Rate limited")
        if resp.status_code == 404:
            raise OllamaModelError("Model not found")
        if resp.status_code >= 500:
            raise OllamaNetworkError(f"Server error {resp.status_code}")
        if resp.status_code != 200:
            raise OllamaError(f"HTTP {resp.status_code}: {resp.text[:200]}")
        try:
            data = resp.json()
        except Exception as e:
            raise OllamaMalformedError(str(e))
        # Ollama chat response: message.content
        msg = data.get("message") or {}
        content = msg.get("content")
        if content is None:
            # fallback for generate endpoint
            content = data.get("response")
        if not isinstance(content, str):
            raise OllamaMalformedError("Missing content in response")
        return content

    async def list_models(self) -> list[str]:
        if not self.api_key:
            raise OllamaAuthError("No API key")
        url = f"{self.base_url}/api/tags"
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(url, headers=self._headers())
        except Exception as e:
            raise OllamaNetworkError(str(e))
        if resp.status_code != 200:
            raise OllamaError(f"HTTP {resp.status_code}")
        data = resp.json()
        models = data.get("models") or []
        return [m.get("name") for m in models if m.get("name")]

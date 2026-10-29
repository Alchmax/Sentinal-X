import httpx
import pytest

from app.ai.ollama_client import (
    OllamaAuthError,
    OllamaClient,
    OllamaMalformedError,
    OllamaModelError,
    OllamaNetworkError,
    OllamaRateLimitError,
)


@pytest.mark.asyncio
async def test_missing_config():
    c = OllamaClient(api_key="", model="")
    assert not c.is_configured()
    with pytest.raises(OllamaAuthError):
        await c.chat([{"role": "user", "content": "hi"}])


def _mock(monkeypatch, status_code, json_body=None, raise_exc=None):
    sc = status_code
    jb = json_body
    rx = raise_exc

    class FakeClient:
        def __init__(self, *a, **k):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def post(self, *a, **k):
            if rx:
                raise rx

            class Resp:
                pass

            r = Resp()
            r.status_code = sc
            r.text = "err"

            def _json():
                return jb or {}

            r.json = _json
            return r

        async def get(self, *a, **k):
            if rx:
                raise rx

            class Resp:
                pass

            r = Resp()
            r.status_code = sc
            r.text = "err"

            def _json():
                return jb or {}

            r.json = _json
            return r

    monkeypatch.setattr(httpx, "AsyncClient", FakeClient)


@pytest.mark.asyncio
async def test_auth_failure(monkeypatch):
    _mock(monkeypatch, 401)
    c = OllamaClient(api_key="k", model="m", base_url="http://x")
    with pytest.raises(OllamaAuthError):
        await c.chat([{"role": "user", "content": "hi"}])


@pytest.mark.asyncio
async def test_rate_limit(monkeypatch):
    _mock(monkeypatch, 429)
    c = OllamaClient(api_key="k", model="m", base_url="http://x")
    with pytest.raises(OllamaRateLimitError):
        await c.chat([{"role": "user", "content": "hi"}])


@pytest.mark.asyncio
async def test_model_not_found(monkeypatch):
    _mock(monkeypatch, 404)
    c = OllamaClient(api_key="k", model="m", base_url="http://x")
    with pytest.raises(OllamaModelError):
        await c.chat([{"role": "user", "content": "hi"}])


@pytest.mark.asyncio
async def test_timeout(monkeypatch):
    _mock(monkeypatch, 200, raise_exc=httpx.TimeoutException("t"))
    c = OllamaClient(api_key="k", model="m", base_url="http://x")
    with pytest.raises(OllamaNetworkError):
        await c.chat([{"role": "user", "content": "hi"}])


@pytest.mark.asyncio
async def test_malformed_response(monkeypatch):
    _mock(monkeypatch, 200, json_body={"foo": "bar"})
    c = OllamaClient(api_key="k", model="m", base_url="http://x")
    with pytest.raises(OllamaMalformedError):
        await c.chat([{"role": "user", "content": "hi"}])


@pytest.mark.asyncio
async def test_success(monkeypatch):
    _mock(monkeypatch, 200, json_body={"message": {"content": "hello"}})
    c = OllamaClient(api_key="k", model="m", base_url="http://x")
    out = await c.chat([{"role": "user", "content": "hi"}])
    assert out == "hello"

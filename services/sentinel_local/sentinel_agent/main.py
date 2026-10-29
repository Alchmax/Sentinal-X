import os
import hmac
import hashlib
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from pathlib import Path

app = FastAPI(title="Sentinel X Local Agent", version="0.1.0")
TOKEN = os.getenv("LOCAL_AGENT_TOKEN", "")

class HashRequest(BaseModel):
    path: str

def _check_token(token: str | None):
    if not TOKEN:
        return
    if not token or not hmac.compare_digest(token, TOKEN):
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/health")
def health():
    return {"status": "ok", "agent": "sentinel-local", "version": "0.1.0"}

@app.post("/hash")
def hash_file(req: HashRequest, x_agent_token: str | None = Header(default=None)):
    _check_token(x_agent_token)
    # path traversal defense
    p = Path(req.path).resolve()
    if not p.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return {"path": str(p), "sha256": h.hexdigest(), "size": p.stat().st_size}
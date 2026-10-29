import hashlib
import mimetypes
from pathlib import Path

SIGNATURES = {
    b"\x89PNG\r\n\x1a\n": ("png", "image/png"),
    b"\xff\xd8\xff": ("jpg", "image/jpeg"),
    b"%PDF": ("pdf", "application/pdf"),
    b"PK\x03\x04": ("zip", "application/zip"),
    b"\x7fELF": ("elf", "application/x-elf"),
    b"MZ": ("exe", "application/x-msdownload"),
    b"\x1f\x8b": ("gz", "application/gzip"),
    b"SQLite format 3\x00": ("sqlite", "application/x-sqlite3"),
}


def detect_signature(head: bytes) -> tuple[str, str]:
    for magic, (ext, mime) in SIGNATURES.items():
        if head.startswith(magic):
            return ext, mime
    return "", ""


def sha256_stream(path: str, chunk_size: int = 65536) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def analyze_file(path: str, max_bytes: int = 50 * 1024 * 1024) -> dict:
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(path)
    size = p.stat().st_size
    if size > max_bytes:
        raise ValueError(f"File exceeds max size {max_bytes}")
    # read head
    with open(path, "rb") as f:
        head = f.read(16)
    ext = p.suffix.lower().lstrip(".")
    detected_ext, mime = detect_signature(head)
    mismatch = bool(detected_ext) and detected_ext != ext
    mismatch_reason = ""
    if mismatch:
        mismatch_reason = (
            f"Extension '{ext}' does not match detected signature '{detected_ext}'"
        )
    # metadata: basic
    metadata = {
        "mtime": p.stat().st_mtime,
        "ctime": p.stat().st_ctime,
    }
    warnings = []
    if mismatch:
        warnings.append(mismatch_reason)
    if size == 0:
        warnings.append("Empty file")
    sha = sha256_stream(path)
    return {
        "filename": p.name,
        "size_bytes": size,
        "sha256": sha,
        "extension": ext,
        "detected_signature": detected_ext,
        "mime_guess": mime or mimetypes.guess_type(p.name)[0] or "",
        "mismatch": mismatch,
        "mismatch_reason": mismatch_reason,
        "metadata": metadata,
        "warnings": warnings,
    }

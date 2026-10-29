import hashlib
import os
import tempfile

from app.services.file_forensics import analyze_file, sha256_stream


def test_sha256_correctness():
    content = b"hello sentinel"
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(content)
        path = f.name
    try:
        assert sha256_stream(path) == hashlib.sha256(content).hexdigest()
        r = analyze_file(path)
        assert r["sha256"] == hashlib.sha256(content).hexdigest()
        assert r["size_bytes"] == len(content)
    finally:
        os.remove(path)


def test_signature_png_mismatch():
    # PNG magic with .txt extension
    data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 10
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        f.write(data)
        path = f.name
    try:
        r = analyze_file(path)
        assert r["detected_signature"] == "png"
        assert r["mismatch"] is True
        assert "png" in r["mismatch_reason"]
    finally:
        os.remove(path)


def test_empty_file():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        path = f.name
    try:
        r = analyze_file(path)
        assert r["size_bytes"] == 0
        assert "Empty file" in r["warnings"]
    finally:
        os.remove(path)


def test_oversized():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"x")
        path = f.name
    try:
        import pytest

        with pytest.raises(ValueError):
            analyze_file(path, max_bytes=0)
    finally:
        os.remove(path)

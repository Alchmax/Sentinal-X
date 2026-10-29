import hashlib
import os
from pathlib import Path
from typing import Any


def hash_file(path: str) -> str:
    try:
        st = os.stat(path)
        if st.st_size > 10 * 1024 * 1024:  # Skip files > 10MB
            return "skipped_large_file"
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except (OSError, PermissionError):
        return "error"


def build_baseline(root: str, max_files: int = 10000) -> list[dict[str, Any]]:
    entries = []
    root_p = Path(root)
    if not root_p.is_dir():
        raise ValueError(f"Not a directory: {root}")
    count = 0
    skip_dirs = {"AppData", "node_modules", ".git", "__pycache__", "Temp", "Cache"}
    for dirpath, dirnames, filenames in os.walk(root_p):
        # Skip heavy directories
        dirnames[:] = [d for d in dirnames if d not in skip_dirs and not d.startswith('.')]
        for name in filenames:
            if count >= max_files:
                break
            full = Path(dirpath) / name
            try:
                st = full.stat()
                entries.append(
                    {
                        "path": str(full),
                        "size": st.st_size,
                        "mtime": st.st_mtime,
                        "sha256": hash_file(str(full)),
                    }
                )
                count += 1
            except (OSError, PermissionError):
                continue
        if count >= max_files:
            break
    return entries


def compare_baseline(baseline: list[dict[str, Any]], root: str) -> dict[str, Any]:
    current = build_baseline(root)
    cur_map = {e["path"]: e for e in current}
    base_map = {e["path"]: e for e in baseline}
    added = [p for p in cur_map if p not in base_map]
    deleted = [p for p in base_map if p not in cur_map]
    modified = []
    unchanged = 0
    for p, base in base_map.items():
        cur = cur_map.get(p)
        if cur is None:
            continue
        if (
            cur["size"] != base["size"]
            or cur["mtime"] != base["mtime"]
            or cur["sha256"] != base["sha256"]
        ):
            modified.append({"path": p, "before": base, "after": cur})
        else:
            unchanged += 1
    return {
        "added": added,
        "deleted": deleted,
        "modified": modified,
        "unchanged": unchanged,
        "current_count": len(current),
        "baseline_count": len(baseline),
    }

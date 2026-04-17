"""Regex search across text files under the working directory."""

import re
from pathlib import Path

from config import settings
from indexing.manifest import DEFAULT_IGNORE_DIRS


def _is_probably_binary(sample: bytes) -> bool:
    if not sample:
        return False
    if b"\x00" in sample[:8192]:
        return True
    text_chars = sum(1 for b in sample[:4096] if 32 <= b < 127 or b in (9, 10, 13))
    return text_chars / max(len(sample[:4096]), 1) < 0.6


def grep_project(
    pattern: str,
    *,
    directory: str | None = None,
    max_hits: int | None = None,
    working_directory: str | None = None,
) -> str:
    """Search files for regex `pattern`; paths are relative to working_directory."""
    root = Path(working_directory or settings.WORKING_DIR).resolve()
    sub = directory or "."
    search_root = (root / sub).resolve()
    if root not in search_root.parents and search_root != root:
        return "error: directory escapes working directory"
    if not search_root.is_dir():
        return f"error: not a directory: {directory or '.'}"

    try:
        regex = re.compile(pattern)
    except re.error as exc:
        return f"error: invalid regex: {exc}"

    cap = max_hits if max_hits is not None else settings.MAX_GREP_HITS
    max_bytes = settings.MAX_GREP_FILE_BYTES
    ignores = DEFAULT_IGNORE_DIRS
    hits = []

    for path in search_root.rglob("*"):
        if path.is_dir():
            continue
        try:
            rel = path.relative_to(root)
        except ValueError:
            continue
        parts = rel.parts
        if any(p in ignores for p in parts):
            continue
        if not path.is_file():
            continue
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if size > max_bytes:
            continue
        try:
            raw = path.read_bytes()
        except OSError:
            continue
        if _is_probably_binary(raw[:8192]):
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            try:
                text = raw.decode("latin-1")
            except UnicodeDecodeError:
                continue

        rel_str = str(rel).replace("\\", "/")
        for lineno, line in enumerate(text.splitlines(), start=1):
            if regex.search(line):
                hits.append(f"{rel_str}:{lineno}:{line.rstrip()}")
                if len(hits) >= cap:
                    break
        if len(hits) >= cap:
            break

    if not hits:
        return "No matches."
    extra = ""
    if len(hits) >= cap:
        extra = f"\n(truncated at {cap} hits)"
    return "\n".join(hits) + extra

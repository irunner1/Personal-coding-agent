"""File manifest JSON for the working directory."""

import json
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel

from config import Settings
from memory_store import coding_agent_root

DEFAULT_IGNORE_DIRS = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        ".venv",
        "venv",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "node_modules",
        ".coding_agent",
    }
)


class FileEntry(BaseModel):
    path: str
    size: int
    mtime: float


def build_manifest(
    settings: Settings, *, ignore_dirs: frozenset[str] | None = None
) -> dict:
    """Walk WORKING_DIR and return a JSON-serializable manifest dict."""
    root = Path(settings.WORKING_DIR).resolve()
    ignores = ignore_dirs if ignore_dirs is not None else DEFAULT_IGNORE_DIRS

    files = []
    for path in root.rglob("*"):
        try:
            rel = path.relative_to(root)
        except ValueError:
            continue
        parts = rel.parts
        if any(p in ignores or (p.startswith(".") and p != ".") for p in parts[:-1]):
            continue
        if path.is_dir() or not path.is_file():
            continue
        try:
            st = path.stat()
        except OSError:
            continue
        files.append(
            FileEntry(
                path=str(rel).replace("\\", "/"),
                size=st.st_size,
                mtime=st.st_mtime,
            )
        )

    files.sort(key=lambda e: e.path)
    return {
        "version": 1,
        "root": str(root),
        "generated_at": datetime.now().isoformat(),
        "file_count": len(files),
        "files": [e.model_dump() for e in files],
    }


def manifest_json_path(settings: Settings) -> Path:
    return coding_agent_root(settings) / settings.INDEX_FILENAME


def write_manifest(
    settings: Settings, *, ignore_dirs: frozenset[str] | None = None
) -> Path:
    """Build manifest and write JSON next to other agent files; return path written."""
    root = coding_agent_root(settings)
    root.mkdir(parents=True, exist_ok=True)
    data = build_manifest(settings, ignore_dirs=ignore_dirs)
    out = manifest_json_path(settings)
    out.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return out

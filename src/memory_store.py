"""Persistent memory file under WORKING_DIR/.coding_agent/."""

from pathlib import Path

from config import Settings


def coding_agent_root(settings: Settings) -> Path:
    return Path(settings.WORKING_DIR).resolve() / settings.CODING_AGENT_DIR


def memory_path(settings: Settings) -> Path:
    return coding_agent_root(settings) / settings.MEMORY_FILENAME


def load_memory_text(settings: Settings) -> str | None:
    path = memory_path(settings)
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def clear_memory_file(settings: Settings) -> bool:
    path = memory_path(settings)
    if not path.is_file():
        return False
    path.unlink()
    return True


def ensure_coding_agent_dir(settings: Settings) -> Path:
    root = coding_agent_root(settings)
    root.mkdir(parents=True, exist_ok=True)
    return root

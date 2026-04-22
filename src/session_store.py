"""Persist chat sessions under WORKING_DIR/.coding_agent/sessions/."""

import json
from pathlib import Path

from google.genai import types

from config import Settings
from memory_store import coding_agent_root


def session_path(settings: Settings, name: str) -> Path:
    safe = name.replace("/", "_").replace("\\", "_").strip() or "default"
    return coding_agent_root(settings) / settings.SESSIONS_SUBDIR / f"{safe}.json"


def save_session(
    path: Path,
    provider: str,
    ollama_messages: list[dict] | None = None,
    gemini_turns: list[dict[str, str]] | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "format_version": 1,
        "provider": provider,
    }
    if ollama_messages is not None:
        data["ollama_messages"] = ollama_messages
    if gemini_turns is not None:
        data["gemini_turns"] = gemini_turns
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_session(path: Path) -> dict | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def gemini_state_from_turns(turns: list[dict[str, str]]) -> list[types.Content]:
    contents = []
    for turn in turns:
        user = turn.get("user", "")
        assistant = turn.get("assistant", "")
        contents.append(
            types.Content(role="user", parts=[types.Part.from_text(text=user)])
        )
        contents.append(
            types.Content(role="model", parts=[types.Part.from_text(text=assistant)])
        )
    return contents

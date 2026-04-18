from pathlib import Path

import pytest

import src.call_function as call_function
from src.call_function import execute_tool


def test_unknown_function(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(call_function.settings, "WORKING_DIR", str(tmp_path))
    assert execute_tool("not_a_real_tool", {}) == {
        "error": "Unknown function: not_a_real_tool",
    }


def test_dispatches_get_files_info(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(call_function.settings, "WORKING_DIR", str(tmp_path))
    (tmp_path / "readme.txt").write_text("x")
    out = execute_tool("get_files_info", {"directory": "."})
    assert "result" in out
    assert "readme.txt" in out["result"]


def test_invalid_arguments_return_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(call_function.settings, "WORKING_DIR", str(tmp_path))
    out = execute_tool("get_file_content", {})
    assert "error" in out
    assert "Invalid arguments" in out["error"]


def test_grep_project_finds_match(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(call_function.settings, "WORKING_DIR", str(tmp_path))
    (tmp_path / "a.txt").write_text("hello world\n", encoding="utf-8")
    out = execute_tool("grep_project", {"pattern": "hello"})
    assert "result" in out
    assert "a.txt" in out["result"]
    assert "hello" in out["result"]

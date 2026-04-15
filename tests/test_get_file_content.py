from pathlib import Path

import pytest

import src.functions.get_file_content as get_file_content_module
from src.functions.get_file_content import get_file_content


def test_reads_small_file(tmp_path: Path) -> None:
    (tmp_path / "f.txt").write_text("hello world")
    result = get_file_content(str(tmp_path), "f.txt")
    assert result == "hello world"


def test_missing_file(tmp_path: Path) -> None:
    result = get_file_content(str(tmp_path), "nope.txt")
    assert "not found" in result.lower()


def test_truncates_when_longer_than_limit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(get_file_content_module.settings, "MAX_FILE_CONTENTS_LENGTH", 5)
    (tmp_path / "big.txt").write_text("abcdefghij")
    result = get_file_content(str(tmp_path), "big.txt")
    assert result.startswith("abcde")
    assert "truncated" in result

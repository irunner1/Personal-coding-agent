from pathlib import Path

from src.functions.write_file import write_file


def test_writes_new_file(tmp_path: Path) -> None:
    body = "hello"
    result = write_file(str(tmp_path), "out.txt", body)
    assert f'Successfully wrote to "out.txt" ({len(body)} characters written)' in result
    assert (tmp_path / "out.txt").read_text() == body


def test_writes_nested_path(tmp_path: Path) -> None:
    result = write_file(str(tmp_path), "nested/out.txt", "x")
    assert "Successfully wrote" in result
    assert (tmp_path / "nested" / "out.txt").read_text() == "x"


def test_rejects_path_outside_workdir(tmp_path: Path) -> None:
    result = write_file(str(tmp_path), "../escape.txt", "bad")
    assert "Cannot write to" in result
    assert not (tmp_path.parent / "escape.txt").exists()

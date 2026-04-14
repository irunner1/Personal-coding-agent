from pathlib import Path

from functions.get_files_info import get_files_info


def test_lists_current_directory(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("hi")
    (tmp_path / "b.txt").write_text("x")
    result = get_files_info(str(tmp_path), ".")
    lines = result.splitlines()
    assert lines[0] == "Result for current directory:"
    body = sorted(lines[1:])
    assert "- a.txt: file_size=2, is_dir=False" in body
    assert "- b.txt: file_size=1, is_dir=False" in body


def test_lists_subdirectory(tmp_path: Path) -> None:
    sub = tmp_path / "pkg"
    sub.mkdir()
    (sub / "mod.py").write_text("# x")
    result = get_files_info(str(tmp_path), "pkg")
    assert "mod.py" in result
    assert "is_dir=False" in result


def test_rejects_escape_above_root(tmp_path: Path) -> None:
    result = get_files_info(str(tmp_path), "../")
    assert "outside the permitted working directory" in result


def test_rejects_non_directory(tmp_path: Path) -> None:
    f = tmp_path / "not_a_dir"
    f.write_text("x")
    result = get_files_info(str(tmp_path), "not_a_dir")
    assert "is not a directory" in result

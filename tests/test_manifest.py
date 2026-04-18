from pathlib import Path

from config import Settings
from indexing.manifest import build_manifest, write_manifest


def test_build_manifest_lists_files(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("x", encoding="utf-8")
    sub = tmp_path / "pkg"
    sub.mkdir()
    (sub / "b.py").write_text("y", encoding="utf-8")

    settings = Settings(WORKING_DIR=str(tmp_path))
    data = build_manifest(settings)
    paths = {f["path"] for f in data["files"]}
    assert "a.txt" in paths
    assert "pkg/b.py" in paths
    assert data["file_count"] == 2


def test_write_manifest_creates_json(tmp_path: Path) -> None:
    (tmp_path / "f.txt").write_text("z", encoding="utf-8")
    settings = Settings(WORKING_DIR=str(tmp_path))
    out = write_manifest(settings)
    assert out.is_file()
    assert "f.txt" in out.read_text(encoding="utf-8")

from pathlib import Path

import pytest


@pytest.fixture
def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def playground_dir(repo_root: Path) -> Path:
    path = repo_root / "playground_calculator"
    assert path.is_dir(), f"Missing fixture project: {path}"
    return path

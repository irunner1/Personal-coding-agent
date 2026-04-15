from unittest.mock import MagicMock

import pytest

import src.main as main_module
from src.config import Settings
from src.prompts import MODE_GENERAL


def test_parse_args_defaults() -> None:
    args = main_module.parse_args(["hello"])
    assert args.user_prompt == "hello"
    assert args.mode == MODE_GENERAL
    assert args.verbose is False
    assert args.provider is None


def test_parse_args_flags() -> None:
    args = main_module.parse_args(
        ["do it", "--mode", "plan", "--verbose", "--provider", "ollama"]
    )
    assert args.user_prompt == "do it"
    assert args.mode == "plan"
    assert args.verbose is True
    assert args.provider == "ollama"


def test_main_passes_through_settings_when_no_provider_flag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[Settings] = []

    def spy_create(s: Settings) -> MagicMock:
        captured.append(s)
        return MagicMock()

    monkeypatch.setattr(main_module, "create_provider", spy_create)
    base = Settings(LLM_PROVIDER="gemini", GEMINI_API_KEY="k")
    monkeypatch.setattr(main_module, "settings", base)

    main_module.main(["just prompt"])

    assert len(captured) == 1
    assert captured[0] is base


def test_main_overrides_provider_from_cli(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: list[Settings] = []

    def spy_create(s: Settings) -> MagicMock:
        captured.append(s)
        return MagicMock()

    monkeypatch.setattr(main_module, "create_provider", spy_create)
    monkeypatch.setattr(
        main_module,
        "settings",
        Settings(LLM_PROVIDER="gemini", GEMINI_API_KEY="k"),
    )

    main_module.main(["task", "--provider", "ollama"])

    assert captured[0].LLM_PROVIDER == "ollama"

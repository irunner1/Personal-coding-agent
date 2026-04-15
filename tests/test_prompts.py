from src.prompts import (
    MODE_ARCH,
    MODE_DEBUG,
    MODE_GENERAL,
    MODE_PLAN,
    build_system_prompt,
)


def test_plan_mode_includes_planning_rules() -> None:
    text = build_system_prompt(MODE_PLAN)
    assert "## Planning mode" in text
    assert "get_files_info" in text


def test_general_mode_omits_planning_section() -> None:
    text = build_system_prompt(MODE_GENERAL)
    assert "## Planning mode" not in text


def test_architecture_mode() -> None:
    text = build_system_prompt(MODE_ARCH)
    assert "## Architecture mode" in text


def test_debug_mode() -> None:
    text = build_system_prompt(MODE_DEBUG)
    assert "## Debug mode" in text


def test_invalid_mode_falls_back_to_general() -> None:
    text = build_system_prompt("not-a-real-mode")
    assert text == build_system_prompt(MODE_GENERAL)

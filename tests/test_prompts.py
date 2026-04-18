from src.prompts import (
    MODE_AGENT,
    MODE_ARCHITECTURE,
    MODE_DEBUG,
    MODE_PLAN,
    BASE_SYSTEM_PROMPT,
    build_system_prompt,
)


def test_plan_mode_includes_planning_rules() -> None:
    text = build_system_prompt(MODE_PLAN)
    assert "## Planning mode" in text
    assert "get_files_info" in text


def test_general_mode_uses_agent_pack() -> None:
    text = build_system_prompt(MODE_AGENT)
    assert "## Planning mode" not in text
    assert "## Agent mode" in text


def test_agent_alias_matches_general() -> None:
    assert build_system_prompt(MODE_AGENT) == build_system_prompt(MODE_AGENT)


def test_architecture_alias_matches_arch() -> None:
    assert build_system_prompt(MODE_ARCHITECTURE) == build_system_prompt(
        MODE_ARCHITECTURE
    )


def test_architecture_mode() -> None:
    text = build_system_prompt(MODE_ARCHITECTURE)
    assert "## Architecture mode" in text


def test_debug_mode() -> None:
    text = build_system_prompt(MODE_DEBUG)
    assert "## Debug mode" in text


def test_invalid_mode_falls_back_to_general() -> None:
    text = build_system_prompt("not-a-real-mode")
    assert BASE_SYSTEM_PROMPT in text


def test_memory_text_appended() -> None:
    text = build_system_prompt(MODE_AGENT, memory_text="remember: use pytest")
    assert "Persistent memory" in text
    assert "remember: use pytest" in text

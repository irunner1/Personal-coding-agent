from unittest.mock import Mock

import pytest

from config import Settings
from src.chat.chat_loop import run_chat


@pytest.fixture
def mock_provider():
    provider = Mock()
    provider.new_chat_state.return_value = {"initial": "state"}
    provider.run_chat.return_value = "Response"
    return provider


@pytest.fixture
def mock_settings():
    settings = Mock(spec=Settings)
    settings.LLM_PROVIDER = "ollama"
    return settings


@pytest.fixture
def mock_chat_deps(monkeypatch):
    def _mock(load_session_return=None, is_file=True, session_data=None):
        printed = []
        inputs = ["Hello", "/exit"]
        input_gen = (x for x in inputs)

        monkeypatch.setattr('builtins.input', lambda _: next(input_gen))
        monkeypatch.setattr(
            'builtins.print', lambda *a, **k: printed.append(a[0] if a else "")
        )

        mock_path = Mock()
        mock_path.is_file.return_value = is_file
        monkeypatch.setattr('src.chat.chat_loop.session_path', lambda s, n: mock_path)
        monkeypatch.setattr(
            'src.chat.chat_loop.load_session',
            lambda p: session_data if session_data is not None else load_session_return,
        )
        monkeypatch.setattr('src.chat.chat_loop.load_memory_text', lambda s: "memory")
        monkeypatch.setattr(
            'src.chat.chat_loop.build_system_prompt', lambda m, memory_text: "prompt"
        )
        monkeypatch.setattr('src.chat.chat_loop.save_session', lambda p, **k: None)
        monkeypatch.setattr('src.chat.chat_loop.gemini_state_from_turns', lambda t: {})

        return printed, mock_path

    return _mock


def test_run_chat_resume_session_invalid_data(
    mock_provider, mock_settings, mock_chat_deps
):
    printed, _ = mock_chat_deps(load_session_return=None, is_file=True)
    run_chat(mock_provider, mock_settings, "standard", False, "session", True)
    assert "Could not resume session; starting fresh." in printed
    mock_provider.new_chat_state.assert_called_once()


def test_run_chat_resume_session_ollama(mock_provider, mock_settings, monkeypatch):
    printed = []
    inputs = ["New message", "/exit"]
    input_gen = (x for x in inputs)

    monkeypatch.setattr('builtins.input', lambda _: next(input_gen))
    monkeypatch.setattr(
        'builtins.print', lambda *a, **k: printed.append(a[0] if a else "")
    )

    mock_path = Mock()
    mock_path.is_file.return_value = True
    monkeypatch.setattr('src.chat.chat_loop.session_path', lambda s, n: mock_path)

    session_data = {
        "provider": "ollama",
        "ollama_messages": [{"role": "user", "content": "Previous message"}],
    }
    mock_load_session = Mock(return_value=session_data)
    monkeypatch.setattr('src.chat.chat_loop.load_session', mock_load_session)
    monkeypatch.setattr('src.chat.chat_loop.load_memory_text', lambda s: "memory")
    monkeypatch.setattr(
        'src.chat.chat_loop.build_system_prompt', lambda m, memory_text: "prompt"
    )
    monkeypatch.setattr('src.chat.chat_loop.save_session', lambda p, **k: None)
    monkeypatch.setattr('src.chat.chat_loop.gemini_state_from_turns', lambda t: {})

    run_chat(mock_provider, mock_settings, "standard", False, "existing_session", True)

    mock_load_session.assert_called_once_with(mock_path)
    assert any("Resumed Ollama session" in str(msg) for msg in printed)


def test_run_chat_resume_session_gemini(monkeypatch):
    from providers.gemini_provider import GeminiProvider

    mock_provider = Mock(spec=GeminiProvider)
    mock_provider.new_chat_state.return_value = {"new": "state"}
    mock_provider.run_chat.return_value = "Response"

    mock_settings = Mock(spec=Settings)
    mock_settings.LLM_PROVIDER = "gemini"

    printed = []
    inputs = ["New message", "/exit"]
    input_gen = (x for x in inputs)

    monkeypatch.setattr('builtins.input', lambda _: next(input_gen))
    monkeypatch.setattr(
        'builtins.print', lambda *a, **k: printed.append(a[0] if a else "")
    )

    mock_path = Mock()
    mock_path.is_file.return_value = True
    monkeypatch.setattr('src.chat.chat_loop.session_path', lambda s, n: mock_path)

    session_data = {
        "provider": "gemini",
        "gemini_turns": [{"user": "Hi", "assistant": "Hello"}],
    }
    monkeypatch.setattr('src.chat.chat_loop.load_session', lambda p: session_data)
    monkeypatch.setattr('src.chat.chat_loop.load_memory_text', lambda s: "memory")
    monkeypatch.setattr(
        'src.chat.chat_loop.build_system_prompt', lambda m, memory_text: "prompt"
    )
    monkeypatch.setattr('src.chat.chat_loop.save_session', lambda p, **k: None)

    mock_gemini_state = Mock(return_value={"restored": "state"})
    monkeypatch.setattr('src.chat.chat_loop.gemini_state_from_turns', mock_gemini_state)

    run_chat(mock_provider, mock_settings, "standard", False, "existing_session", True)

    mock_gemini_state.assert_called_once_with(
        [
            {"user": "Hi", "assistant": "Hello"},
            {'user': 'New message', 'assistant': 'Response'},
        ]
    )
    assert any("Resumed Gemini session" in str(msg) for msg in printed)


def test_run_chat_resume_session_not_found(mock_provider, mock_settings, monkeypatch):
    inputs = ["Hello", "/exit"]
    input_gen = (x for x in inputs)

    monkeypatch.setattr('builtins.input', lambda _: next(input_gen))
    monkeypatch.setattr('builtins.print', lambda *a, **k: None)

    mock_path = Mock()
    mock_path.is_file.return_value = False
    monkeypatch.setattr('src.chat.chat_loop.session_path', lambda s, n: mock_path)
    monkeypatch.setattr('src.chat.chat_loop.load_session', Mock())
    monkeypatch.setattr('src.chat.chat_loop.load_memory_text', lambda s: "memory")
    monkeypatch.setattr(
        'src.chat.chat_loop.build_system_prompt', lambda m, memory_text: "prompt"
    )
    monkeypatch.setattr('src.chat.chat_loop.save_session', lambda p, **k: None)
    monkeypatch.setattr('src.chat.chat_loop.gemini_state_from_turns', lambda t: {})

    run_chat(
        mock_provider, mock_settings, "standard", False, "nonexistent_session", True
    )
    mock_provider.new_chat_state.assert_called_once()


def test_run_chat_resume_session_incompatible_provider(
    mock_provider, mock_settings, monkeypatch
):
    printed = []
    inputs = ["Hello", "/exit"]
    input_gen = (x for x in inputs)

    monkeypatch.setattr('builtins.input', lambda _: next(input_gen))
    monkeypatch.setattr(
        'builtins.print', lambda *a, **k: printed.append(a[0] if a else "")
    )

    mock_path = Mock()
    mock_path.is_file.return_value = True
    monkeypatch.setattr('src.chat.chat_loop.session_path', lambda s, n: mock_path)

    session_data = {
        "provider": "gemini",
        "gemini_turns": [{"user": "Hi", "assistant": "Hello"}],
    }
    monkeypatch.setattr('src.chat.chat_loop.load_session', lambda p: session_data)
    monkeypatch.setattr('src.chat.chat_loop.load_memory_text', lambda s: "memory")
    monkeypatch.setattr(
        'src.chat.chat_loop.build_system_prompt', lambda m, memory_text: "prompt"
    )
    monkeypatch.setattr('src.chat.chat_loop.save_session', lambda p, **k: None)
    monkeypatch.setattr('src.chat.chat_loop.gemini_state_from_turns', lambda t: {})

    run_chat(mock_provider, mock_settings, "standard", False, "gemini_session", True)

    assert any(
        "Session file is for Gemini; starting fresh with Ollama." in str(msg)
        for msg in printed
    )
    mock_provider.new_chat_state.assert_called_once()
    assert any(
        "Session file is for Gemini; starting fresh with Ollama." in str(msg)
        for msg in printed
    )
    mock_provider.new_chat_state.assert_called_once()

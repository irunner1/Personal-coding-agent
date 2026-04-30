"""Ollama chat keeps the first system message in sync with the latest system_instruction."""

from unittest.mock import MagicMock, patch

from config import Settings
from providers.ollama_provider import OllamaProvider


def test_ollama_run_chat_updates_leading_system_message() -> None:
    settings = Settings()
    with patch("providers.ollama_provider.Client"):
        prov = OllamaProvider(settings)
    prov.client = MagicMock()
    prov.client.chat.return_value = MagicMock(
        message=MagicMock(tool_calls=None, content="ok")
    )
    state: list[dict] = [{"role": "system", "content": "old"}]
    prov.run_chat(state, "hi", "new-system", max_turns=5)
    assert state[0]["content"] == "new-system"
    assert state[1] == {"role": "user", "content": "hi"}

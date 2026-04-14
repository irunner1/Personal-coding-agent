import pytest

from config import Settings
from providers import create_provider
from providers.gemini_provider import GeminiProvider
from providers.ollama_provider import OllamaProvider


def test_create_gemini_provider() -> None:
    settings = Settings(LLM_PROVIDER="gemini", GEMINI_API_KEY="test-key")
    provider = create_provider(settings)
    assert isinstance(provider, GeminiProvider)


def test_create_ollama_provider() -> None:
    settings = Settings(LLM_PROVIDER="ollama")
    provider = create_provider(settings)
    assert isinstance(provider, OllamaProvider)


def test_rejects_unknown_provider() -> None:
    bad = Settings.model_construct(LLM_PROVIDER="other")
    with pytest.raises(ValueError, match="Unknown LLM_PROVIDER"):
        create_provider(bad)

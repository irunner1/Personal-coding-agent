from config import Settings
from providers.gemini_provider import GeminiProvider
from providers.ollama_provider import OllamaProvider


def create_provider(settings: Settings) -> OllamaProvider | GeminiProvider:
    if settings.LLM_PROVIDER == "ollama":
        return OllamaProvider(settings)
    if settings.LLM_PROVIDER == "gemini":
        return GeminiProvider(settings)
    raise ValueError(
        f"Unknown LLM_PROVIDER {settings.LLM_PROVIDER!r}; use 'gemini' or 'ollama'."
    )


__all__ = ["create_provider", "GeminiProvider", "OllamaProvider"]

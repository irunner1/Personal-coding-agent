"""Service settings."""

from typing import Literal

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    MAX_FILE_CONTENTS_LENGTH: int = 1000
    WORKING_DIR: str = "./playground"
    LLM_PROVIDER: Literal["gemini", "ollama"] = "ollama"

    # Project agent data (under WORKING_DIR)
    CODING_AGENT_DIR: str = ".coding_agent"
    MEMORY_FILENAME: str = "memory.md"
    INDEX_FILENAME: str = "index.json"
    SESSIONS_SUBDIR: str = "sessions"

    # grep_project limits
    MAX_GREP_FILE_BYTES: int = 512_000
    MAX_GREP_HITS: int = 200

    # Google
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_API_KEY: str | None = None

    # Ollama
    OLLAMA_MODEL: str = "gemma4"
    OLLAMA_HOST: str | None = None


settings = Settings()

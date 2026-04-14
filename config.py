from typing import Literal

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    MAX_FILE_CONTENTS_LENGTH: int = 1000
    WORKING_DIR: str = "./playground_calculator"
    LLM_PROVIDER: Literal["gemini", "ollama"] = "ollama"

    # Google
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_API_KEY: str | None = None

    # Ollama
    OLLAMA_MODEL: str = "gemma4"
    OLLAMA_HOST: str | None = None


settings = Settings()

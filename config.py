from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class Settings(BaseModel):
    MAX_FILE_CONTENTS_LENGTH: int = 1000
    WORKING_DIR: str = "./calculator"
    LLM_PROVIDER: str = "gemini"
    GEMINI_MODEL: str = "gemini-2.5-flash"


settings = Settings()

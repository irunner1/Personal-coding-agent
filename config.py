from pydantic import BaseModel


class Settings(BaseModel):
    MAX_FILE_CONTENTS_LENGTH: int = 1000
    WORKING_DIR = "./calculator"


settings = Settings()

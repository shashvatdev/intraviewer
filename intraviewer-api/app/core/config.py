from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "Intraviewer API"
    APP_VERSION: str = "1.0.0"
    DATABASE_URL: str = "postgresql://localhost:5432/intraviewer"
    GROQ_API_KEY: Optional[str] = None
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

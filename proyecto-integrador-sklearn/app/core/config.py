from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
import json
import secrets


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )

    # App
    PROJECT_NAME: str = "RikiNode AI Service"
    API_V1_STR: str = "/api/v1"
    VERSION: str = "1.0.0"

    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Auth (demo)
    ADMIN_EMAIL: str = "admin@rikinode.com"
    ADMIN_PASSWORD: str = "admin123"

    # Model
    MODEL_PATH: str = "./models/sentiment_model.joblib"
    MODEL_NAME: str = "tfidf-logreg-sentiment-v1"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [i.strip() for i in v.strip("[]").split(",")]
        return v

    # Automation
    ENABLE_SCHEDULER: bool = True
    HEALTH_CHECK_INTERVAL_MINUTES: int = 5


settings = Settings()

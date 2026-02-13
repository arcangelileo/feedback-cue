import logging

from pydantic_settings import BaseSettings
from functools import lru_cache

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    app_name: str = "FeedbackCue"
    secret_key: str = "change-me-to-a-random-secret-key"
    database_url: str = "sqlite+aiosqlite:///./data/feedbackcue.db"
    environment: str = "development"

    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24 hours

    host: str = "0.0.0.0"
    port: int = 8000

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if settings.environment == "production" and settings.secret_key == "change-me-to-a-random-secret-key":
        raise ValueError(
            "SECRET_KEY must be changed from default in production! "
            'Generate one with: python -c "import secrets; print(secrets.token_urlsafe(32))"'
        )
    return settings

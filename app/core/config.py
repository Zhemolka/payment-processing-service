from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "payment-processing-service"
    api_key: str = "test-secret-api-key"
    database_url: str = "postgresql+asyncpg://payment:payment@localhost:5432/payments"
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"

    outbox_poll_interval: float = Field(default=1.0, gt=0)
    outbox_batch_size: int = Field(default=50, ge=1, le=500)
    webhook_timeout: float = Field(default=5.0, gt=0)
    processing_max_attempts: int = Field(default=3, ge=1, le=10)
    processing_retry_base_delay: float = Field(default=1.0, gt=0)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

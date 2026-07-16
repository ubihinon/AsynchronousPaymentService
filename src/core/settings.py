import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    API_URL: str = "api/v1"
    API_KEY: str = "123"
    LOG_LEVEL: str = "error"
    DEBUG: bool = False

    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "payment_service_db"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@0.0.0.0:5432/postgres"
    SYNC_DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@0.0.0.0:5432/postgres"

    RABBITMQ_HOST: str = "rabbitmq"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASS: str = "guest"
    RABBITMQ_URL: str = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/"

    OUTBOX_LIMIT: int = 10

    HOST: str = "0.0.0.0"
    PORT: int = 8000


    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True
    )


settings = Settings()

from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MODE: Literal["DEV", "TEST", "PROD"]
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    # Postgresql
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    TEST_DB_HOST: str
    TEST_DB_PORT: int
    TEST_DB_USER: str
    TEST_DB_PASS: str
    TEST_DB_NAME: str

    # Auth
    SECRET_KEY: str
    ALGORITHM: str

    # Redis
    REDIS_HOST: str
    REDIS_PORT: int

    # email notification
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASS: str

    @property
    def DATABASE_URL(self):
        return "postgresql+asyncpg://{}:{}@{}:{}/{}".format(
            self.DB_USER,
            self.DB_PASS,
            self.DB_HOST,
            self.DB_PORT,
            self.DB_NAME,
        )

    @property
    def TEST_DATABASE_URL(self):
        return "postgresql+asyncpg://{}:{}@{}:{}/{}".format(
            self.TEST_DB_USER,
            self.TEST_DB_PASS,
            self.TEST_DB_HOST,
            self.TEST_DB_PORT,
            self.TEST_DB_NAME,
        )

    # Настройки приложения
    API_V1_PREFIX: str = "/api/v1"
    TITLE: str = "Шаблонизатор документов"
    VERSION: str = "0.0.1"
    DESCRIPTION: str = "Шаблонизатор документов"
    DOCS_URL: str | None = f"{API_V1_PREFIX}/docs"
    REDOC_URL: str | None = f"{API_V1_PREFIX}/redoc"
    OPENAPI_URL: str | None = f"{API_V1_PREFIX}/openapi"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )


settings = Settings()

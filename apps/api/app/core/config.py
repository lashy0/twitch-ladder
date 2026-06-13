from pydantic import PostgresDsn, RedisDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        env_file_encoding="utf-8",
    )

    # App
    PROJECT_NAME: str = "Twitch Ladder API"
    DEBUG: bool = False

    API_V1_PREFIX: str = "/api/v1"

    # CORS
    CORS_ALLOW_ORIGINS: list[str] = ["http://localhost:3000"]

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "text"  # text | json
    LOG_BACKTRACE: bool = False
    LOG_DIAGNOSE: bool = False

    # Postgres
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: SecretStr = SecretStr("")
    POSTGRES_DB: str = ""

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: SecretStr = SecretStr("")
    REDIS_DB: int = 0

    # Twitch (App token)
    TWITCH_CLIENT_ID: str = ""
    TWITCH_CLIENT_SECRET: SecretStr = SecretStr("")
    TWITCH_AUTH_BASE_URL: str = "https://id.twitch.tv"
    TWITCH_HELIX_BASE_URL: str = "https://api.twitch.tv/helix"
    TWITCH_GQL_URL: str = "https://gql.twitch.tv/gql"
    TWITCH_GQL_CLIENT_ID: str = ""
    TWITCH_HTTP_TIMEOUT_SECONDS: float = 10.0

    @property
    def database_url(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD.get_secret_value(),
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    @property
    def redis_url(self) -> RedisDsn:
        return RedisDsn.build(
            scheme="redis",
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            path=str(self.REDIS_DB),
            password=self.REDIS_PASSWORD.get_secret_value()
            if self.REDIS_PASSWORD
            else None,
        )


settings = Settings()

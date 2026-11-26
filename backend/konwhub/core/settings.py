from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Validated deployment settings with no credential defaults."""
    
    model_config = SettingsConfigDict(env_prefix="KONWHUB_", env_file=".env", extra="ignore")

    app_name: str = "KonwHub"
    environment: str = "development"
    api_prefix: str = "/api/v1"
    session_ttl_seconds: int = Field(default=3600, ge=60)
    session_cookie_name: str = "satoken"
    database_url: str | None = None
    redis_url: str | None = None
    elasticsearch_url: str | None = None
    minio_endpoint: str | None = None
    minio_bucket: str | None = None
    neo4j_url: str | None = None
    dingtalk_signing_secret: str | None = None
    chat_model: str | None = None
    embedding_model: str | None = None
    provider_api_key: str | None = None
    required_secrets: tuple[str, ...] = ()

    def validate_required_secrets(self) -> None:
        missing = [name for name in self.required_secrets if not getattr(self, name, None)]
        if missing:
            raise ValueError(f"Missing required deployment settings: {', '.join(missing)}")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_required_secrets()
    return settings

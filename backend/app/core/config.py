from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://budget:budget_dev@localhost/family_budget"
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = "change-me-in-production"
    anthropic_api_key: str = ""
    bigquery_project: str = ""
    mapbox_token: str = ""
    environment: str = "development"
    # AES-256 key for encrypting personal data columns (32 bytes, base64-encoded)
    encryption_key: str = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
    # Comma-separated list of allowed CORS origins
    cors_origins: str = "http://localhost:3000"

    model_config = {"env_file": ".env"}


settings = Settings()

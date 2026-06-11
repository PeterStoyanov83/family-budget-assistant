from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://localhost/family_budget"
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = "change-me-in-production"
    anthropic_api_key: str = ""
    bigquery_project: str = ""
    mapbox_token: str = ""
    environment: str = "development"

    class Config:
        env_file = ".env"


settings = Settings()

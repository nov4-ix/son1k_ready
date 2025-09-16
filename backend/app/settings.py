import os
from pydantic import BaseSettings, AnyHttpUrl

class Settings(BaseSettings):
    PROJECT_NAME: str = "Son1kVers3 Suno Bridge"
    API_PREFIX: str = "/api"
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-me")
    POSTGRES_DSN: str = os.getenv("POSTGRES_DSN", "postgresql+psycopg2://postgres:postgres@db:5432/postgres")

settings = Settings()

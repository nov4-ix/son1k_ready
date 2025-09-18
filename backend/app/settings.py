import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "Son1kVers3 Suno Bridge"
    API_PREFIX: str = "/api"
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-me")
    POSTGRES_DSN: str = os.getenv("POSTGRES_DSN", "sqlite:///./son1k.db")

settings = Settings()


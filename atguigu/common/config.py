from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    """AI Service 运行配置。"""

    ai_database_url: str = (
        "postgresql+psycopg://customer_service:customer_service"
        "@127.0.0.1:5432/ai_customer_service_v1"
    )
    api_host: str = "0.0.0.0"
    api_port: int = 8002
    internal_service_token: str = "customer-internal-token"
    jwt_secret: str = "ecommerce-secret"
    jwt_algorithm: str = "HS256"
    llm_model: str = ""
    prompt_version: str = "customer-support-v1"

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

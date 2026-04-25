from pathlib import Path
import os
from typing import Any

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.secrets import get_secret

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

# Secret IDs pedidos en la entrega
DB_URL_SECRET_ID = "livemenu-db-url"
SECRET_KEY_SECRET_ID = "livemenu-secret-key"
GCS_BUCKET_SECRET_ID = "livemenu-gcs-bucket"


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str | None = None

    # Security
    SECRET_KEY: str | None = None
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://livemenu.duckdns.org",
    ]

    # Rate limiting (RNF04)
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 100

    # Storage
    STORAGE_TYPE: str = "local"
    STORAGE_PATH: str = "./uploads"
    GCP_BUCKET_NAME: str | None = None

    # Worker Pool
    WORKER_POOL_SIZE: int = 4

    # GCP
    GCP_PROJECT_ID: str | None = None

    # Environment
    ENVIRONMENT: str = "development"

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        case_sensitive=True,
        extra="ignore",
    )

    @model_validator(mode="before")
    @classmethod
    def load_secrets_in_production(cls, values: Any) -> Any:
        if not isinstance(values, dict):
            return values

        environment = str(values.get("ENVIRONMENT", "development")).lower()

        if environment == "production":
            project_id = (
                values.get("GCP_PROJECT_ID")
                or os.getenv("GCP_PROJECT_ID")
                or os.getenv("GOOGLE_CLOUD_PROJECT")
            )
            if not project_id:
                raise ValueError(
                    "GCP_PROJECT_ID or GOOGLE_CLOUD_PROJECT is required in production"
                )

            values = dict(values)
            values["GCP_PROJECT_ID"] = project_id
            values["DATABASE_URL"] = get_secret(DB_URL_SECRET_ID, project_id)
            values["SECRET_KEY"] = get_secret(SECRET_KEY_SECRET_ID, project_id)
            values["GCP_BUCKET_NAME"] = get_secret(GCS_BUCKET_SECRET_ID, project_id)

        return values


settings = Settings()
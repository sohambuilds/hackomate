from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment.

    - MONGODB_URI: required
    - DB_NAME: defaults to "hackathon_twin"
    """

    mongodb_uri: str = Field(..., alias="MONGODB_URI")
    db_name: str = Field("hackathon_twin", alias="DB_NAME")

    # Load from .env if present; ignore unknown env vars
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("mongodb_uri")
    @classmethod
    def validate_mongodb_uri(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError(
                "MONGODB_URI environment variable is required and cannot be empty."
            )
        return value


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


__all__ = ["Settings", "get_settings"]



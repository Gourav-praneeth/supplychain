from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.
    Uses pydantic-settings for validation and type conversion.
    """

    DATABASE_URL: str
    POLYGON_AMOY_RPC_URL: str
    CONTRACT_ADDRESS: str
    PINATA_API_KEY: str
    PINATA_SECRET_API_KEY: str

    PINATA_BASE_URL: str = "https://api.pinata.cloud"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

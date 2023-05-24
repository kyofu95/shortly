"""
This module contains configuration variables for the application.
Requires environment variables to be set before app start.
"""

from pydantic import BaseSettings


class AppSettings(BaseSettings):
    """Base settings class"""

    TITLE: str = "Shortly"
    VERSION: str = "0.5.0"

    ENVIRONMENT: str
    DEBUG: bool

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRY: int = 25
    JWT_REFRESH_TOKEN_EXPIRY: int = 60 * 60 * 20

    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOWED_ORIGINS: list[str] = ["*"]
    CORS_ALLOWED_METHODS: list[str] = ["*"]
    CORS_ALLOWED_HEADERS: list[str] = ["*"]

    class Config:
        case_sensitive = True
        allow_mutation = False


settings = AppSettings()

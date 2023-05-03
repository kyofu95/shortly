"""
This module contains configuration variables for the application.
Requires environment variables to be set before app start.
"""

from pydantic import BaseSettings


class AppSettings(BaseSettings):
    """Base settings class"""

    ENVIRONMENT: str
    DEBUG: bool

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DATABASE: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    class Config:
        case_sensitive = True
        allow_mutation = False


settings = AppSettings()

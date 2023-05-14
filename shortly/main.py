"""This module contains the main logic of the app."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shortly.api.endpoints import api_router
from shortly.core.config import settings


def initialize_app() -> FastAPI:
    """Configurate FastAPI"""

    api = FastAPI(debug=settings.DEBUG, title=settings.TITLE, version=settings.VERSION)

    api.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOWED_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOWED_METHODS,
        allow_headers=settings.CORS_ALLOWED_HEADERS,
    )

    @api.on_event("startup")
    async def startup() -> None:
        pass

    @api.on_event("shutdown")
    async def shutdown() -> None:
        pass

    api.include_router(api_router)

    return api


app = initialize_app()

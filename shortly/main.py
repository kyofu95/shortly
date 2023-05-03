"""This module contains the main logic of the app."""

from fastapi import FastAPI

from shortly.api.endpoints import api_router
from shortly.core.config import settings


def initialize_app() -> FastAPI:
    """Configurate FastAPI"""

    api = FastAPI(debug=settings.DEBUG)

    @api.on_event("startup")
    async def startup() -> None:
        pass

    @api.on_event("shutdown")
    async def shutdown() -> None:
        pass

    api.include_router(api_router)

    return api


app = initialize_app()

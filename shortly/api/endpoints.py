"""This module joins various routes and includes them into one single router."""

from fastapi.routing import APIRouter

from .health import router as health_router
from .v1.users import router as users_router
from .v1.links import router as links_router
from .v1.auth import router as auth_router

api_router = APIRouter(prefix="/api")

api_router.include_router(health_router)

api_router.include_router(users_router)
api_router.include_router(links_router)
api_router.include_router(auth_router)

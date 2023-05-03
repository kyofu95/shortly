"""
This module provides a route for checking the status of the health of the application.
"""

import asyncio
from fastapi import Depends, Response, status
from fastapi.routing import APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shortly.core.database import get_session

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
async def get_health(session: AsyncSession = Depends(get_session)):
    """Endpoint to check if the API is running smoothly."""

    try:
        asyncio.wait_for(session.execute(select(1)), timeout=1)
    except asyncio.TimeoutError:
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    return {"status": "ok"}

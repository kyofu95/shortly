"""
This module provides a route for checking the status of the health of the application.
"""

import asyncio
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shortly.core.database import get_session
import shortly.schemas.health as health_schemas

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=health_schemas.Health, status_code=status.HTTP_200_OK)
async def get_health(session: AsyncSession = Depends(get_session)):
    """Endpoint to check if the API is running smoothly."""

    try:
        await asyncio.wait_for(session.execute(select(1)), timeout=1)
    except asyncio.TimeoutError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE) from exc
    return {"status": "ok"}

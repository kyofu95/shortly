"""This module contains repository helper function."""

from typing import Callable, Type

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shortly.core.database import get_session
from shortly.repository.base import BaseRepository


def get_repository(repository_type: Type[BaseRepository]) -> Callable[[AsyncSession], BaseRepository]:
    """Helper dependency function. Returns repository."""

    def _get_repo(session: AsyncSession = Depends(get_session)) -> BaseRepository:
        return repository_type(session)

    return _get_repo
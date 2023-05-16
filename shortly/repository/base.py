"""This module contains abstaract repository class for dependency chain."""

from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    """Base repository class."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

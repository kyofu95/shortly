"""This module provides repository for link data."""

from datetime import datetime
import string
import random

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from shortly.models.link import Link
from shortly.schemas.link import LinkInDB
from .base import BaseRepository


class LinkDoesNotExists(Exception):
    """Raised when no appropriate link record found."""


class GenerationFailed(Exception):
    """Raised when no short key were created."""


ALPHANUMERIC: str = string.ascii_letters + string.digits


class LinkRepository(BaseRepository):
    """Repository responsible for CRUD operations on Links table."""

    async def create(self, original_url: str, user_id: int) -> LinkInDB:
        """Generate short key and return a link."""
        max_retries = 5
        while True:
            try:
                key = "".join(random.choices(ALPHANUMERIC, k=7))
                db_link = Link(short_key=key, original_url=original_url, user_id=user_id)

                self.session.add(db_link)
                await self.session.commit()
                await self.session.refresh(db_link)
            except IntegrityError as exc:
                await self.session.rollback()
                max_retries -= 1
                if not max_retries:
                    raise GenerationFailed() from exc
            else:
                break

        return db_link

    async def disable_by_key_and_user_id(self, link_key: str, user_id: int) -> None:
        """Disable already existing link by key and user id."""
        results = await self.session.execute(
            select(Link).where((Link.short_key == link_key) & (Link.user_id == user_id) & (Link.disabled.is_(False)))
        )
        db_link = results.scalar()
        if not db_link:
            raise LinkDoesNotExists()

        db_link.disabled = True
        db_link.last_access_date = datetime.now()
        await self.session.commit()

    async def get_all_by_user_id(self, user_id: int) -> list[LinkInDB]:
        """Get all links by user id."""
        results = await self.session.execute(select(Link).where((Link.user_id == user_id) & (Link.disabled.is_(False))))
        return results.scalars().all()

    async def get_by_key_and_user_id(self, link_key: str, user_id: int) -> LinkInDB | None:
        """Get a link by short key and user id."""
        results = await self.session.execute(
            select(Link).where((Link.short_key == link_key) & (Link.user_id == user_id) & (Link.disabled.is_(False)))
        )
        return results.scalar()

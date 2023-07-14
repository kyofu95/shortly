"""This module provides repository for link data."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from shortly.models.link import Link, links_id_seq
from shortly.schemas.link import LinkInDB
from .base import BaseRepository


class LinkDoesNotExists(Exception):
    """Raised when no appropriate link record found."""


class GenerationFailed(Exception):
    """Raised when no short key were created."""


class LinkRepository(BaseRepository):
    """Repository responsible for CRUD operations on Links table."""

    async def create(self, link_id: int, key: str, original_url: str, user_id: int) -> LinkInDB:
        """Create link and store it in a database."""
        try:
            db_link = Link(id=link_id, short_key=key, original_url=original_url, user_id=user_id)

            self.session.add(db_link)
            await self.session.commit()
            await self.session.refresh(db_link)
        except IntegrityError as exc:
            await self.session.rollback()
            raise GenerationFailed() from exc

        return db_link

    async def get_id_from_sequence(self) -> int:
        """Retrieves the next value from the links_id_seq sequence and returns it as an integer."""
        results = await self.session.execute(select(links_id_seq.next_value()))
        return results.scalar_one()

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

    async def get_by_key(self, link_key: str) -> LinkInDB | None:
        """Get a link by short key and user id."""
        results = await self.session.execute(
            select(Link).where((Link.short_key == link_key) & (Link.disabled.is_(False)))
        )
        return results.scalar()

    async def increase_view_counter_by_key(self, link_key: str) -> None:
        """Increases link view counter by one."""
        db_link = await self.get_by_key(link_key)
        db_link.view_count += 1

        await self.session.commit()

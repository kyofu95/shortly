"""Contains Link database model."""

from datetime import datetime
from typing import Callable, Optional, TYPE_CHECKING

from sqlalchemy import ForeignKey, func, String, Sequence
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

# Avoid pylint warnings
if TYPE_CHECKING:
    from .user import User

    func: Callable

links_id_seq = Sequence("links_id_seq", start=500_000)


class Link(Base):
    """Represents 'links' database table."""

    __tablename__ = "links"

    id: Mapped[int] = mapped_column(links_id_seq, primary_key=True)
    short_key: Mapped[str] = mapped_column(String(7), unique=True, index=True)
    original_url: Mapped[str] = mapped_column()
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    create_date: Mapped[datetime] = mapped_column(default=func.now())
    expiry_date: Mapped[Optional[datetime]]
    last_access_date: Mapped[datetime] = mapped_column(default=func.now())
    view_count: Mapped[int] = mapped_column(default=0)
    disabled: Mapped[bool] = mapped_column(default=False)

    user: Mapped["User"] = relationship(back_populates="links", lazy="selectin")

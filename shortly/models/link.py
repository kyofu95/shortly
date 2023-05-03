"""Contains Link database model."""

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import ForeignKey, func, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Link(Base):
    """Represents 'links' database table."""

    __tablename__ = "links"

    id: Mapped[int] = mapped_column(primary_key=True)
    short_key: Mapped[str] = mapped_column(String(7), unique=True, index=True)
    original_url: Mapped[str] = mapped_column()
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    create_date: Mapped[datetime] = mapped_column(default=func.now())
    expiry_date: Mapped[Optional[datetime]]
    view_count: Mapped[int]
    disabled: Mapped[bool] = mapped_column(default=False)

    user: Mapped["User"] = relationship(back_populates="links", lazy="selectin")

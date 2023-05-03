"""Contains User database model."""

from datetime import datetime
from typing import Callable, TYPE_CHECKING

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

# Avoid pylint warnings
if TYPE_CHECKING:
    from .link import Link

    func: Callable


class User(Base):
    """Represents 'users' database table."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    create_at: Mapped[datetime] = mapped_column(default=func.now())
    disabled: Mapped[bool] = mapped_column(default=False)

    links: Mapped[list["Link"]] = relationship(back_populates="user", lazy="selectin")

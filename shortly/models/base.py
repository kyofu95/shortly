"""Contains base model"""
from typing import Any

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base model."""

    def dict(self) -> dict[str, Any]:
        """Generate a dictionary representation of the sqlalchemy model."""
        return {field.name: getattr(self, field.name) for field in self.__table__.columns}

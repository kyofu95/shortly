"""This module defines a Pydantic schema for a Token object."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TokenPayload(BaseModel):
    """A Pydantic model representing the payload of a token."""
    token_type: str
    exp: datetime
    iat: Optional[datetime]
    sub: str


class Token(BaseModel):
    """A Pydantic model representing a security token."""
    access_token: str
    refresh_token: str
    token_type: str

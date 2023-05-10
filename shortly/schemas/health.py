"""This module defines a Pydantic schema for a Health object."""

from pydantic import BaseModel


class Health(BaseModel):
    """A Pydantic model representing health response."""

    status: str

    class Config:
        schema_extra = {"example": {"status": "OK"}}

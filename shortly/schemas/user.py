"""This module defines a Pydantic schema for a User object."""

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, constr

if TYPE_CHECKING:
    from .link import LinkInDB, LinkOut


class UserBase(BaseModel):
    login: constr(max_length=50)

    class Config:
        schema_extra = {"example": {"login": "Myname"}}


class UserCreate(UserBase):
    password: constr(max_length=50)

    class Config(UserBase.Config):
        schema_extra = {"example": {"login": "Myname", "password": "MySuperSecurePassword"}}


class UserOut(BaseModel):
    create_at: datetime
    disabled: bool

    links: list["LinkOut"] = []

    class Config:
        orm_mode = True

        schema_extra = {"example": {"create_at": "2023-01-01T02:10:12.777785", "disabled": "False", "links": "[]"}}


class UserInDB(UserBase):
    id: int
    create_at: datetime
    disabled: bool

    links: list["LinkInDB"] = []

    class Config:
        orm_mode = True

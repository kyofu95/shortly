"""This module defines a Pydantic schema for a User object."""

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, constr

if TYPE_CHECKING:
    from .link import LinkInDB, LinkOut


class UserBase(BaseModel):
    login: constr(max_length=50)


class UserCreate(UserBase):
    password: constr(max_length=50)


class UserOut(BaseModel):
    create_at: datetime
    disabled: bool

    links: list["LinkOut"] = []

    class Config:
        orm_mode = True


class UserInDB(UserBase):
    id: int
    create_at: datetime
    disabled: bool

    links: list["LinkInDB"] = []

    class Config:
        orm_mode = True

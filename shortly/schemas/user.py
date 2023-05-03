"""This module defines a Pydantic schema for a User object."""

from datetime import datetime

from pydantic import BaseModel


class UserBase(BaseModel):
    login: str


class UserCreate(UserBase):
    password: str


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

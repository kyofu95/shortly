"""This module defines a Pydantic schema for a Link object."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, constr


class LinkBase(BaseModel):
    short_key: constr(min_length=7, max_length=7)
    original_url: str


class LinkOut(LinkBase):
    create_date: datetime
    expiry_date: Optional[datetime]
    last_access_date: datetime
    view_count: int
    disabled: bool

    class Config:
        orm_mode = True


class LinkInDB(LinkOut):
    id: int
    user_id: int

    user: "UserInDB"

    class Config:
        orm_mode = True

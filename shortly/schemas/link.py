"""This module defines a Pydantic schema for a Link object."""

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from pydantic import AnyUrl, BaseModel, constr

if TYPE_CHECKING:
    from .user import UserInDB


class LinkBase(BaseModel):
    original_url: AnyUrl


class LinkIn(LinkBase):
    pass


class LinkOut(LinkBase):
    short_key: constr(min_length=7, max_length=7, regex=r"[^\W_]+$")
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

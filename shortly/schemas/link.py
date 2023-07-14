"""This module defines a Pydantic schema for a Link object."""

from datetime import datetime
from typing import Optional, TYPE_CHECKING, TypeAlias

from pydantic import AnyUrl, BaseModel, constr

if TYPE_CHECKING:
    from .user import UserInDB


KeyType: TypeAlias = constr(min_length=4, max_length=7, regex=r"[^\W_]+$")


class LinkBase(BaseModel):
    original_url: AnyUrl

    class Config:
        schema_extra = {"example": {"original_url": "http://example.com"}}


class LinkIn(LinkBase):
    pass


class LinkOut(LinkBase):
    short_key: KeyType

    class Config:
        orm_mode = True

        schema_extra = {
            "example": {
                "original_url": "http://example.com",
                "short_key": "hgrt67c",
            }
        }


class LinkStats(LinkBase):
    short_key: KeyType
    create_date: datetime
    expiry_date: Optional[datetime]
    last_access_date: datetime
    view_count: int
    disabled: bool

    class Config:
        orm_mode = True

        schema_extra = {
            "example": {
                "original_url": "http://example.com",
                "short_key": "hgrt67c",
                "create_date": "2023-01-01T02:10:12.777785",
                "expiry_date": "2024-01-01T02:10:12.777785",
                "last_access_date": "2023-05-05T02:10:12.777785",
                "view_count": "1",
                "disabled": "False",
            }
        }


class LinkInDB(LinkStats):
    id: int
    user_id: int

    user: "UserInDB"

    class Config:
        orm_mode = True

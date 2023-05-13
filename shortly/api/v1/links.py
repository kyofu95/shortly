"""This module contains routing for the Links API."""

from datetime import datetime
import random
import string

from fastapi import Depends, HTTPException, Response, status
from fastapi.routing import APIRouter
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from shortly.core.database import get_session
from shortly.models.link import Link as LinkModel
from shortly.models.user import User as UserModel
import shortly.schemas.link as link_schemas
from .auth import get_current_user

router = APIRouter(
    prefix="/links",
    tags=["Links"],
    responses={
        400: {"description": "Bad request"},
        401: {"description": "Unauthorized"},
    },
)

ALPHANUMERIC: str = string.ascii_letters + string.digits


@router.post(
    "",
    response_model=link_schemas.LinkOut,
    status_code=status.HTTP_201_CREATED,
    responses={500: {"description": "Internal server error"}},
)
async def create_link(
    new_link: link_schemas.LinkIn,
    response: Response,
    user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    max_retries = 5
    while True:
        try:
            key = "".join(random.choices(ALPHANUMERIC, k=7))
            db_link = LinkModel(short_key=key, original_url=new_link.original_url, user_id=user.id)

            session.add(db_link)
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            max_retries -= 1
            if not max_retries:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from exc
        else:
            break

    response.headers["location"] = router.url_path_for("get_link", key=db_link.short_key)
    return db_link


@router.get("", response_model=list[link_schemas.LinkOut], status_code=status.HTTP_200_OK)
async def get_all_links(
    user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    results = await session.execute(
        select(LinkModel).where((LinkModel.user_id == user.id) & (LinkModel.disabled.is_(False)))
    )
    return results.scalars().all()


@router.get(
    "/{key}",
    response_model=link_schemas.LinkOut,
    status_code=status.HTTP_200_OK,
    responses={404: {"description": "Not found"}},
)
async def get_link(
    key: link_schemas.KeyType,
    user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    results = await session.execute(
        select(LinkModel).where(
            (LinkModel.short_key == key) & (UserModel.id == user.id) & (LinkModel.disabled.is_(False))
        )
    )
    db_link = results.scalar()
    if not db_link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Could not find link by key {key}")
    return db_link


@router.delete(
    "/{key}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Not found"}},
)
async def delete_link(
    key: link_schemas.KeyType, user: UserModel = Depends(get_current_user), session: AsyncSession = Depends(get_session)
):
    results = await session.execute(
        select(LinkModel).where(
            (LinkModel.short_key == key) & (UserModel.id == user.id) & (LinkModel.disabled.is_(False))
        )
    )
    db_link = results.scalar()
    if not db_link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Could not find link by key {key}")

    db_link.disabled = True
    db_link.last_access_date = datetime.now()
    await session.commit()


@router.get(
    "/{key}/stats",
    response_model=link_schemas.LinkStats,
    status_code=status.HTTP_200_OK,
    responses={404: {"description": "Not found"}},
)
async def get_stats(
    key: link_schemas.KeyType, user: UserModel = Depends(get_current_user), session: AsyncSession = Depends(get_session)
):
    results = await session.execute(
        select(LinkModel).where(
            (LinkModel.short_key == key) & (UserModel.id == user.id) & (LinkModel.disabled.is_(False))
        )
    )
    db_link = results.scalar()
    if not db_link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Could not find link by key {key}")

    return db_link

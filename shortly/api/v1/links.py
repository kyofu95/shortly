"""This module contains routing for the Links API."""

from fastapi import Depends, HTTPException, Response, Request, status
from fastapi.routing import APIRouter

from shortly.repository.link import LinkRepository, LinkDoesNotExists
import shortly.service.link as link_service
import shortly.schemas.link as link_schema
import shortly.schemas.user as user_schema
from .Depends.oauth import get_current_user
from .Depends.repo import get_repository


router = APIRouter(
    prefix="/links",
    tags=["Links"],
    responses={
        400: {"description": "Bad request"},
    },
)


@router.post(
    "",
    response_model=link_schema.LinkOut,
    status_code=status.HTTP_201_CREATED,
    responses={401: {"description": "Unauthorized"}, 500: {"description": "Internal server error"}},
)
async def create_link(
    new_link: link_schema.LinkIn,
    request: Request,
    response: Response,
    user: user_schema.UserInDB = Depends(get_current_user),
    link_repository: LinkRepository = Depends(get_repository(LinkRepository)),
):
    """Create a new link."""

    try:
        db_link = await link_service.create(new_link.original_url, user.id, link_repository)
    except link_service.CreateLinkError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from exc

    path = request.url_for("get_link", key=db_link.short_key)
    response.headers["location"] = str(path)
    return db_link


@router.get(
    "",
    response_model=list[link_schema.LinkOut],
    status_code=status.HTTP_200_OK,
    responses={401: {"description": "Unauthorized"}},
)
async def get_all_links(
    user: user_schema.UserInDB = Depends(get_current_user),
    link_repository: LinkRepository = Depends(get_repository(LinkRepository)),
):
    """Get all enabled links created by user."""

    return await link_repository.get_all_by_user_id(user.id)


@router.get(
    "/{key}",
    response_model=link_schema.LinkOut,
    status_code=status.HTTP_200_OK,
    responses={404: {"description": "Not found"}},
)
async def get_link(
    key: link_schema.KeyType,
    link_repository: LinkRepository = Depends(get_repository(LinkRepository)),
):
    """Get specific link by a key."""

    db_link = await link_repository.get_by_key(key)
    if not db_link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Could not find link by key {key}")

    await link_repository.increase_view_counter_by_key(key)

    return db_link


@router.delete(
    "/{key}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={401: {"description": "Unauthorized"}, 404: {"description": "Not found"}},
)
async def delete_link(
    key: link_schema.KeyType,
    user: user_schema.UserInDB = Depends(get_current_user),
    link_repository: LinkRepository = Depends(get_repository(LinkRepository)),
):
    """Disable a link."""

    try:
        await link_repository.disable_by_key_and_user_id(key, user.id)
    except LinkDoesNotExists as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Could not find link by key {key}") from exc


@router.get(
    "/{key}/stats",
    response_model=link_schema.LinkStats,
    status_code=status.HTTP_200_OK,
    responses={404: {"description": "Not found"}},
)
async def get_stats(
    key: link_schema.KeyType,
    link_repository: LinkRepository = Depends(get_repository(LinkRepository)),
):
    """Get link statistics."""

    db_link = await link_repository.get_by_key(key)
    if not db_link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Could not find link by key {key}")

    return db_link

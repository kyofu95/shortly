"""This module contains routing for the Users API."""

from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter

from shortly.repository.user import UserRepository
import shortly.schemas.user as user_schemas
from .auth import get_current_user
from .deps import get_repository


router = APIRouter(prefix="/users", tags=["Users"], responses={400: {"description": "Bad request"}})


@router.post(
    "",
    response_model=user_schemas.UserOut,
    status_code=status.HTTP_201_CREATED,
    name="create a new user",
)
async def create_user(
    new_user: user_schemas.UserCreate,
    user_repository: UserRepository = Depends(get_repository(UserRepository)),
):
    """Create a new user."""

    # check if user already exists and active
    db_user = await user_repository.get_by_login(new_user.login)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this login already exists")

    # create user
    db_user = await user_repository.create(new_user.login, new_user.password)

    return db_user


@router.get(
    "/me",
    response_model=user_schemas.UserOut,
    response_model_exclude={"links"},
    status_code=status.HTTP_200_OK,
    name="get current user",
    responses={401: {"description": "Unauthorized"}},
)
async def get_user_me(user: user_schemas.UserInDB = Depends(get_current_user)):
    """Get current user."""

    return user


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={401: {"description": "Unauthorized"}},
)
async def delete_user(
    user: user_schemas.UserInDB = Depends(get_current_user),
    user_repository: UserRepository = Depends(get_repository(UserRepository)),
):
    """Disables current user."""

    await user_repository.disable(user.id)

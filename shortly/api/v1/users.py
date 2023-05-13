"""This module contains routing for the Users API."""

from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shortly.core.database import get_session
from shortly.core.security import Hasher
from shortly.models.user import User as UserModel
import shortly.schemas.user as user_schemas
from .auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"], responses={400: {"description": "Bad request"}})


@router.post(
    "",
    response_model=user_schemas.UserOut,
    status_code=status.HTTP_201_CREATED,
    name="create a new user",
)
async def create_user(new_user: user_schemas.UserCreate, session: AsyncSession = Depends(get_session)):
    # check if user already exists and active
    results = await session.execute(
        select(UserModel).where((UserModel.login == new_user.login) & (UserModel.disabled.is_(False)))
    )
    db_user = results.scalar()
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this login already exists")

    # create user
    hashed_password = Hasher.get_password_hash(new_user.password)

    db_user = UserModel(login=new_user.login, password=hashed_password)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@router.get(
    "/me",
    response_model=user_schemas.UserOut,
    response_model_exclude={"links"},
    status_code=status.HTTP_200_OK,
    name="get current user",
    responses={401: {"description": "Unauthorized"}},
)
async def get_user_me(user: UserModel = Depends(get_current_user)):
    return user


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={401: {"description": "Unauthorized"}},
)
async def delete_user(user: UserModel = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    user.disabled = True
    user.refresh_token = ""
    await session.commit()

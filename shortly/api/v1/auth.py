"""This module provides a function for acquiring an OAuth2 access token."""

from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shortly.core.database import get_session
from shortly.core.security import Hasher, generate_token, decode_token, TokenType
from shortly.models.user import User as UserModel
from shortly.schemas.token import Token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

router = APIRouter(tags=["OAuth2"], responses={401: {"description": "Unauthorized"}})


def create_tokens(user_id: int) -> Token:
    try:
        access_token = generate_token(TokenType.ACCESS, user_id)
        refresh_token = generate_token(TokenType.REFRESH, user_id)
    except ValueError as exc:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail=str(exc), headers={"WWW-Authenticate": "Bearer"}
        ) from exc

    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


@router.post(
    "/token",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    responses={500: {"description": "Internal server error"}},
)
async def get_tokens(form: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_session)):
    # verify if user exists and is not disabled
    results = await session.execute(
        select(UserModel).where((UserModel.login == form.username) & (UserModel.disabled.is_(False)))
    )
    db_user = results.scalar()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    # validate password
    if not Hasher.verify_password(form.password, db_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    token = create_tokens(db_user.id)

    db_user.refresh_token = token.refresh_token
    await session.commit()

    return token


async def get_current_user_from_token(token: str, token_type: str, session: AsyncSession) -> UserModel:
    # decode token
    payload = decode_token(token)

    if not payload.token_type == token_type:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token type mismatch")

    # verify user
    results = await session.execute(
        select(UserModel).where((UserModel.id == int(payload.sub)) & (UserModel.disabled.is_(False)))
    )
    db_user = results.scalar()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if token_type == "refresh_token" and db_user.refresh_token != token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token does not match the stored one",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return db_user


async def get_current_user(
    access_token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)
) -> UserModel:
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    return await get_current_user_from_token(access_token, "access_token", session)


async def get_current_user_with_refresh_token(
    refresh_token: str, session: AsyncSession = Depends(get_session)
) -> UserModel:
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    return await get_current_user_from_token(refresh_token, "refresh_token", session)


@router.post(
    "/refresh-token",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    responses={400: {"description": "Bad request"}},
)
async def get_refresh_token(current_user: UserModel = Depends(get_current_user_with_refresh_token)):
    return create_tokens(current_user.id)

"""This module contains Oauth2 functions."""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

import shortly.schemas.user as user_schema
from shortly.core.security import generate_token, decode_token, TokenType
from shortly.schemas.token import Token
from shortly.repository.user import UserRepository
from .repo import get_repository


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")


def create_tokens(user_id: int) -> Token:
    """Creates access and refresh tokens."""
    try:
        access_token = generate_token(TokenType.ACCESS, user_id)
        refresh_token = generate_token(TokenType.REFRESH, user_id)
    except ValueError as exc:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail=str(exc), headers={"WWW-Authenticate": "Bearer"}
        ) from exc

    return Token(access_token=access_token, refresh_token=refresh_token, token_type="Bearer")


async def get_current_user_from_token(
    token: str, token_type: TokenType, user_repository: UserRepository
) -> user_schema.UserInDB:
    """Decodes token and returns an associated user."""

    # decode token
    payload = decode_token(token)

    if not payload.token_type == token_type.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token type mismatch")

    # verify user
    db_user = await user_repository.get_by_id(int(payload.sub))
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if token_type == TokenType.REFRESH and db_user.refresh_token != token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token does not match the stored one",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return db_user


async def get_current_user(
    access_token: str = Depends(oauth2_scheme),
    user_repository: UserRepository = Depends(get_repository(UserRepository)),
) -> user_schema.UserInDB:
    """Dependency helper. Returns user from access token."""

    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    return await get_current_user_from_token(access_token, TokenType.ACCESS, user_repository)


async def get_current_user_with_refresh_token(
    refresh_token: str, user_repository: UserRepository = Depends(get_repository(UserRepository))
) -> user_schema.UserInDB:
    """Dependency helper. Returns user from refresh token."""

    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    return await get_current_user_from_token(refresh_token, TokenType.REFRESH, user_repository)

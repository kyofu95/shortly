"""This module provides a function for acquiring an OAuth2 access token."""

from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from shortly.core.security import generate_token, decode_token, TokenType
from shortly.schemas.token import Token

import shortly.schemas.user as user_schema
from shortly.repository.user import UserRepository, PasswordDoesNotMatch, UserDoesNotExists
from .deps import get_repository


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

router = APIRouter(tags=["OAuth2"], responses={401: {"description": "Unauthorized"}})


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


@router.post(
    "/token",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    responses={500: {"description": "Internal server error"}},
)
async def get_tokens(
    form: OAuth2PasswordRequestForm = Depends(),
    user_repository: UserRepository = Depends(get_repository(UserRepository)),
):
    """Autenticates user and creates tokens."""

    # verify if user exists and is not disabled
    try:
        db_user = await user_repository.get_by_login_authentication(form.username, form.password)
    except (PasswordDoesNotMatch, UserDoesNotExists) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password") from exc

    token = create_tokens(db_user.id)

    await user_repository.update_refresh_token_by_id(token.refresh_token, db_user.id)

    return token


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


@router.post(
    "/refresh-token",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    responses={400: {"description": "Bad request"}},
)
async def get_refresh_token(
    current_user: user_schema.UserInDB = Depends(get_current_user_with_refresh_token),
    user_repository: UserRepository = Depends(get_repository(UserRepository)),
):
    """Updates tokens."""

    tokens = create_tokens(current_user.id)
    await user_repository.update_refresh_token_by_id(tokens.refresh_token, current_user.id)
    return tokens

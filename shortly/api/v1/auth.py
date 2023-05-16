"""This module provides a function for acquiring an OAuth2 access token."""

from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordRequestForm

import shortly.schemas.user as user_schema
from shortly.schemas.token import Token
from shortly.repository.user import UserRepository, PasswordDoesNotMatch, UserDoesNotExists
from .Depends.repo import get_repository
from .Depends.oauth import create_tokens, get_current_user_with_refresh_token


router = APIRouter(tags=["OAuth2"], responses={401: {"description": "Unauthorized"}})


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

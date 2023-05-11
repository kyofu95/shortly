"""This module provides a function for acquiring an OAuth2 access token."""
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError, JWTClaimsError
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shortly.core.config import settings
from shortly.core.database import get_session
from shortly.core.security import Hasher
from shortly.models.user import User as UserModel
from shortly.schemas.token import Token, TokenPayload
from shortly.schemas.user import UserInDB


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

router = APIRouter(tags=["OAuth2"])


def create_token(token_type: str, delta: timedelta, user_id: int) -> str:
    payload = TokenPayload(
        token_type=token_type,
        exp=datetime.utcnow() + delta,
        iat=datetime.utcnow(),
        sub=str(user_id),
    )

    try:
        token = jwt.encode(payload.dict(), key=settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Token encode failure") from exc
    return token


def decode_token(token: str) -> TokenPayload:
    try:
        payload_dict = jwt.decode(token, key=settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        payload = TokenPayload(**payload_dict)
    except ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except (JWTClaimsError, JWTError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid payload in token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    return payload


def create_tokens(user_id: int) -> Token:
    access_token = create_token("access_token", timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRY), user_id)
    refresh_token = create_token("refresh_token", timedelta(hours=settings.JWT_REFRESH_TOKEN_EXPIRY), user_id)

    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


@router.post(
    "/token",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    responses={401: {"description": "Unauthorized"}, 500: {"description": "Internal server error"}},
)
async def get_access_token(form: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_session)):
    # verify if user exists
    results = await session.execute(
        select(UserModel).where((UserModel.login == form.username) & (UserModel.disabled.is_(False)))
    )
    db_user = results.scalar()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    if db_user.disabled:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")

    # validate password
    if not Hasher.verify_password(form.password, db_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    return create_tokens(db_user.id)


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


@router.post("/refresh-token", response_model=Token)
async def get_refresh_token(current_user: UserModel = Depends(get_current_user_with_refresh_token)):
    return create_tokens(current_user.id)

"""This module provides a function for acquiring an OAuth2 access token."""
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError, JWTClaimsError
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


@router.post("/token", response_model=Token)
async def get_access_token(form: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_session)):
    # verify if user exists
    results = await session.execute(
        select(UserModel).where((UserModel.login == form.username) & (UserModel.disabled.is_(False)))
    )
    db_user = results.scalar()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    # validate password
    if not Hasher.verify_password(form.password, db_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    # create access token
    access_payload = TokenPayload(
        token_type="access_token",
        exp=datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRY),
        iat=datetime.utcnow(),
        sub=str(db_user.id),
    )

    try:
        access_token = jwt.encode(access_payload.dict(), key=settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Token encode failure") from exc

    return {"access_token": access_token, "token_type": "bearer"}


async def get_current_user_from_token(token: str, session: AsyncSession) -> UserInDB:
    # decode token
    try:
        payload_dict = jwt.decode(token, key=settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        payload = TokenPayload(**payload_dict)
    except (JWTClaimsError, ExpiredSignatureError, JWTError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate token") from exc

    # verify user
    results = await session.execute(
        select(UserModel).where((UserModel.id == int(payload.sub)) & (UserModel.disabled.is_(False)))
    )
    db_user = results.scalar()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    return UserInDB(**db_user.dict())


async def get_current_user(
    token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)
) -> UserInDB:
    return await get_current_user_from_token(token, session)

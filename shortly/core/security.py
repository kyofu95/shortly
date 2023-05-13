"""This module provides functions for hashing and verifying passwords and token encode/decode."""

from datetime import datetime, timedelta
from enum import Enum

from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError, JWTClaimsError
from passlib.context import CryptContext
from pydantic import ValidationError

from shortly.schemas.token import TokenPayload
from .config import settings


class TokenType(str, Enum):
    """Enumeration type containing possible token types."""

    ACCESS = "access_token"
    REFRESH = "refresh_token"


class Hasher:
    """Hashing utility."""

    hash_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generate hash value."""
        return Hasher.hash_context.hash(password)

    @staticmethod
    def verify_password(original_password: str, hashed_password: str) -> bool:
        """Verify hash value."""
        return Hasher.hash_context.verify(original_password, hashed_password)


def generate_token(token_type: TokenType, delta: timedelta, user_id: int) -> str:
    """Creates access or refresh token."""

    payload = TokenPayload(
        token_type=token_type.value,
        exp=datetime.utcnow() + delta,
        iat=datetime.utcnow(),
        sub=str(user_id),
    )

    try:
        token = jwt.encode(payload.dict(), key=settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    except JWTError as exc:
        raise ValueError("Token encode failure") from exc
    return token


def decode_token(token: str) -> TokenPayload:
    """Decodes token and return its payload."""

    try:
        payload_dict = jwt.decode(token, key=settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        payload = TokenPayload(**payload_dict)
    except ExpiredSignatureError as exc:
        raise ValueError("Token has been expired") from exc
    except (JWTClaimsError, JWTError) as exc:
        raise ValueError("Could not validate token") from exc
    except ValidationError as exc:
        raise ValueError("Invalid payload in token") from exc
    return payload

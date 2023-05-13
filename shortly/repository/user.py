"""This module provides repository for user data."""

from sqlalchemy import select

from shortly.core.security import Hasher
from shortly.models.user import User
from shortly.schemas.user import UserInDB

from .base import BaseRepository


class UserDoesNotExists(Exception):
    """Raised when no appropriate user record found."""


class PasswordDoesNotMatch(Exception):
    """Raised when users password is different from provided."""


class UserRepository(BaseRepository):
    """Repository responsible for CRUD operations on Users table."""

    async def create(self, login: str, password: str) -> UserInDB:
        """Create user with login and password. Password is hashed inside."""
        hashed_password = Hasher.get_password_hash(password)

        user = User(login=login, password=hashed_password)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def disable(self, user_id: int) -> None:
        """Disable already existing user by user id."""
        # get user
        results = await self.session.execute(select(User).where((User.id == user_id) & (User.disabled.is_(False))))
        user = results.scalar()
        if not user:
            raise UserDoesNotExists()

        # and disable them
        user.disabled = True
        user.refresh_token = ""
        await self.session.commit()

    async def get_by_id(self, user_id: int) -> UserInDB | None:
        """Returns user by provided user ID."""
        results = await self.session.execute(select(User).where((User.id == user_id) & (User.disabled.is_(False))))
        return results.scalar()

    async def get_by_login(self, login: str) -> UserInDB | None:
        """Returns user by provided user login."""
        results = await self.session.execute(select(User).where((User.login == login) & (User.disabled.is_(False))))
        return results.scalar()

    async def get_by_login_authentication(self, login: str, password: str) -> UserInDB:
        """Return authenticated user or throws an exception."""
        user = await self.get_by_login(login)
        if not user:
            raise UserDoesNotExists()

        if not Hasher.verify_password(password, user.password):
            raise PasswordDoesNotMatch()

        return user

    async def update_refresh_token_by_id(self, token: str, user_id: int):
        """Updates refresh_token field."""
        results = await self.session.execute(select(User).where((User.id == user_id) & (User.disabled.is_(False))))
        db_user = results.scalar()
        if not db_user:
            raise UserDoesNotExists()

        db_user.refresh_token = token
        await self.session.commit()

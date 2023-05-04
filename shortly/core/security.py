"""This module provides functions for hashing and verifying passwords."""

from passlib.context import CryptContext


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

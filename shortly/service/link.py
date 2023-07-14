"""This module contains link service."""

import string

from shortly.schemas.link import LinkInDB
from shortly.repository.link import LinkRepository, GenerationFailed

ALPHANUMERIC: str = string.digits + string.ascii_letters
ALPHANUMERIC_LEN: int = len(ALPHANUMERIC)


class CreateLinkError(Exception):
    """Raised when lnik could not be created."""


def encode_base62(number: int) -> str:
    """Encodes a given number into a base62 string."""

    if not number:
        return "0"

    encoded = ""
    while number:
        number, rem = divmod(number, ALPHANUMERIC_LEN)
        encoded = ALPHANUMERIC[rem] + encoded
    return encoded


async def create(original_url: str, user_id: int, repo: LinkRepository) -> LinkInDB:
    """ "
    Creates link.
    """

    link_id = await repo.get_id_from_sequence()

    key = encode_base62(link_id)
    try:
        link = await repo.create(link_id, key, original_url, user_id)
    except GenerationFailed as exc:
        raise CreateLinkError() from exc

    return link

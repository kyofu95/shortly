import string
import random

from shortly.schemas.link import LinkInDB
from shortly.repository.link import LinkRepository, GenerationFailed

ALPHANUMERIC: str = string.ascii_letters + string.digits
MAX_NUM_OF_TRIES = 5


class CreateLinkError(Exception):
    pass


async def create(original_url: str, user_id: int, repo: LinkRepository) -> LinkInDB:
    while True:
        retry_number = MAX_NUM_OF_TRIES
        try:
            key = "".join(random.choices(ALPHANUMERIC, k=7))
            link = await repo.create(key, original_url, user_id)
        except GenerationFailed as exc:
            retry_number -= 1
            if not retry_number:
                raise CreateLinkError() from exc
        else:
            break

    return link
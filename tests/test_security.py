import pytest

from shortly.core.security import Hasher, generate_token, decode_token, TokenType


@pytest.mark.asyncio
async def test_hasher():
    plain_password = "my_super_secure_password"

    hashed_pwd = Hasher.get_password_hash(plain_password)
    assert Hasher.verify_password(plain_password, hashed_pwd)


@pytest.mark.asyncio
async def test_tokens_gen():
    user_id = 10

    token = generate_token(TokenType.ACCESS, user_id)
    payload = decode_token(token)

    assert int(payload.sub) == user_id

    user_id = 1000

    token = generate_token(TokenType.REFRESH, user_id)
    payload = decode_token(token)

    assert int(payload.sub) == user_id

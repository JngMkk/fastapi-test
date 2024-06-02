import asyncio
from functools import wraps
from typing import AsyncGenerator

from aioredis import RedisError, from_url

from app.config import settings
from app.exceptions import ServiceUnavailableException


async def get_redis() -> AsyncGenerator:
    redis = from_url(settings.REDIS_URL, max_connections=5)
    try:
        yield redis
    finally:
        await redis.close()


def retry_on_redis_error(max_retries=3, delay=1):
    """redis 명령어 실패 시 재시도"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return await func(*args, **kwargs)
                except RedisError:
                    retries += 1
                    if retries == max_retries:
                        raise ServiceUnavailableException
                    await asyncio.sleep(delay)

        return wrapper

    return decorator

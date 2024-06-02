from dataclasses import asdict, dataclass
from datetime import datetime
from time import time

from aioredis import Redis
from fastapi import Request, Response
from jose import JWTError, jwt  # type:ignore
from typing_extensions import Self

from app.config import settings
from app.exceptions import InvalidTokenException, UnAuthorizedException
from app.models.users import User

from .redis import retry_on_redis_error


@dataclass(frozen=True)
class TokenPayload:
    sub: str
    exp: int
    is_admin: bool

    @classmethod
    def from_user(cls, user_id: str, expires_in_seconds: int, is_admin: bool) -> Self:
        """datetime을 timestamp로 변환한 뒤 TokenPayload 객체 반환"""

        expires_timestamp = int(time()) + expires_in_seconds
        return cls(sub=user_id, exp=expires_timestamp, is_admin=is_admin)

    def exp_to_datetime(self) -> datetime:
        """expire timestamp to datetime"""

        return datetime.fromtimestamp(self.exp)


class TokenHandler:
    @staticmethod
    def encode_token(token_payload: TokenPayload) -> str:
        return jwt.encode(  # type:ignore
            asdict(token_payload), settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM
        )

    @staticmethod
    def decode_token(token: str) -> TokenPayload:
        """검증 실패 시 InvalidTokenException"""

        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)
            return TokenPayload(**payload)
        except JWTError:
            raise InvalidTokenException

    @classmethod
    def generate_access_token(cls, user: User) -> str:
        expires_in = settings.ACCESS_TOKEN_EXPIRES_SECONDS
        return cls.encode_token(TokenPayload.from_user(user.id, expires_in, user.is_admin))

    @classmethod
    def generate_refresh_token(cls, user: User) -> str:
        expries_in = settings.REFRESH_TOKEN_EXPIRES_SECONDS
        return cls.encode_token(TokenPayload.from_user(user.id, expries_in, user.is_admin))


class TokenStorage:
    @staticmethod
    @retry_on_redis_error()
    async def save_refresh_token(redis: Redis, user: User, token: str) -> None:
        await redis.set(
            f"{settings.REDIS_TOKEN_KEY}:{user.id}",
            value=token,
            ex=settings.REFRESH_TOKEN_EXPIRES_SECONDS,
        )

    @staticmethod
    @retry_on_redis_error()
    async def delete_refresh_token(redis: Redis, token: str) -> None:
        payload = TokenHandler.decode_token(token)
        await redis.delete(f"{settings.REDIS_TOKEN_KEY}:{payload.sub}")

    @staticmethod
    @retry_on_redis_error()
    async def set_blacklist(redis: Redis, token: str) -> None:
        payload = TokenHandler.decode_token(token)
        if (remaining_sec := payload.exp - int(time())) > 0:
            await redis.set(f"{settings.REDIS_BLACKLIST_KEY}:{token}", value=1, ex=remaining_sec)

    @staticmethod
    @retry_on_redis_error()
    async def is_blacklisted(redis: Redis, token: str) -> bool:
        return await redis.exists(f"{settings.REDIS_BLACKLIST_KEY}:{token}") > 0  # type:ignore


class TokenIssuer:
    COOKIE_PATH = "api/"

    def __init__(self, request: Request, response: Response, redis: Redis) -> None:
        self.request = request
        self.response = response
        self.redis = redis

    async def issue_token(self, user: User) -> str:
        """access token 발급, refresh token redis 및 cookie에 저장"""

        access_token = TokenHandler.generate_access_token(user)
        refresh_token = TokenHandler.generate_refresh_token(user)
        await TokenStorage.save_refresh_token(self.redis, user, refresh_token)

        # TODO: 배포할 때 쿠키 설정 신경 쓰기
        self.response.set_cookie(
            settings.REFRESH_TOKEN_COOKIE_KEY,
            refresh_token,
            settings.REFRESH_TOKEN_EXPIRES_SECONDS,
            path=self.COOKIE_PATH,
            httponly=True,
            secure=True,
            samesite=None,
        )
        return access_token

    async def revoke_token(self) -> None:
        """cookie 확인 후 refresh token 있으면 token 삭제"""

        token = self.request.cookies.get(settings.REFRESH_TOKEN_COOKIE_KEY)
        if token is not None:
            await TokenStorage.delete_refresh_token(self.redis, token)
            await TokenStorage.set_blacklist(self.redis, token)
            self.response.delete_cookie(settings.REFRESH_TOKEN_COOKIE_KEY, self.COOKIE_PATH)
        return

    async def rotate_token(self) -> str:
        """cookie 확인 후 토큰 없으면 UnAuthorizedException"""

        token = self.request.cookies.get(settings.REFRESH_TOKEN_COOKIE_KEY)
        if token is None:
            raise UnAuthorizedException
        self.response.delete_cookie(settings.REFRESH_TOKEN_COOKIE_KEY, self.COOKIE_PATH)
        if await TokenStorage.is_blacklisted(self.redis, token):
            raise InvalidTokenException
        await TokenStorage.delete_refresh_token(self.redis, token)
        await TokenStorage.set_blacklist(self.redis, token)
        payload = TokenHandler.decode_token(token)
        return await self.issue_token(User(id=payload.sub))

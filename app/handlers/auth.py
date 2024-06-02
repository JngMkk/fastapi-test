from typing import Any

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.security.utils import get_authorization_scheme_param
from passlib.context import CryptContext  # type:ignore
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.exceptions import (
    ForbiddenException,
    InvalidTokenException,
    NotFoundException,
    UnAuthorizedException,
)
from app.models.users import User

from .db import get_db_session
from .jwt import TokenHandler


class CustomHTTPAuth(HTTPBearer):
    def __init__(self):
        super().__init__(scheme_name=settings.TOKEN_TYPE)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        auth = request.headers.get("Authorization")
        scheme, credentials = get_authorization_scheme_param(auth)
        if not (auth and scheme and credentials):
            raise UnAuthorizedException
        if scheme.lower() != settings.TOKEN_TYPE.lower():
            raise InvalidTokenException

        return HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)


class AuthHandler:
    @staticmethod
    async def get_user(conditions: list[Any], db: AsyncSession) -> User:
        try:
            return await User.get(db, conditions)
        except NotFoundException:
            raise InvalidTokenException

    @classmethod
    async def get_curr_user(
        cls,
        token: HTTPAuthorizationCredentials = Depends(CustomHTTPAuth()),
        db: AsyncSession = Depends(get_db_session),
    ) -> User:
        payload = TokenHandler.decode_token(token.credentials)
        user = await cls.get_user([User.id == payload.sub], db)
        if user.is_disabled:
            raise ForbiddenException
        return user


class PasswordHandler:
    PW_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def hash_password(cls, password: str) -> str:
        """비밀번호 해싱(bcrypt)한 값 반환

        Args:
            password (str): 비밀번호(평문)

        Returns:
            str: 비밀번호 해시값 반환
        """

        return cls.PW_CONTEXT.hash(password)

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """일반 패스워드와 해싱한 패스워드가 일치하는지 비교한 후 True/False 반환

        Args:
            plain_password (str): 비밀번호(평문)
            hashed_password (str): 비밀번호(해시값)

        Returns:
            bool: 일치하면 True 반환
        """

        return cls.PW_CONTEXT.verify(plain_password, hashed_password)

    @staticmethod
    def validate_password(password: str) -> bool:
        """비밀번호 정규식 검사 (pydantic Field에선 전방 탐색과 후방 탐색 동시에 지원 하지 않음.)

        1: 최소 8글자, 최대 20글자.
        2: 영문 대문자, 소문자, 숫자, 특수기호 조합.
        3: 대문자 최소 1개, 소문자 최소 1개, 숫자 최소 1개, 특수기호 최소 1개.

        Args:
            password (str): 비밀번호(평문)

        Returns:
            bool: 정규식과 일치할시 True
        """
        import re

        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,20}$"
        if re.match(pattern, password) is not None:
            return True
        return False

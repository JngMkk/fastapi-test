from datetime import datetime, timedelta

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session, select
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from apps.users.models import User

from .constant.errors import CREDENTIALS_VALIDATE_FAILED, INACTVE_USER
from .database import get_session
from .settings import (
    JWT_ALGORITHM,
    JWT_EXPIRE_KEY,
    JWT_SECRET_KEY,
    JWT_SUBJECT_KEY,
    PW_HASH_ALGORITHM,
    SIGNIN_API_URL,
    TOKEN_EXPIRE_SECONDS,
    TOKEN_TYPE,
)

# * schemes: 해시 알고리즘 list
# * deprecated="auto": 지정 해시 알고리즘을 제외하고 지원되는 모든 알고리즘을 사용하지 않음.
pw_context = CryptContext(schemes=[PW_HASH_ALGORITHM], deprecated="auto")

# * OAuth2PasswordBearer: FastAPI에서 제공하는 보안 로직
# * Application에 보안 로직이 존재함을 알림
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=SIGNIN_API_URL)


class HashPassWord:
    @staticmethod
    def create_hash(password: str) -> str:
        """문자열 해싱한 값 반환"""
        return pw_context.hash(password)  # type:ignore

    @staticmethod
    def check_password(plain_password: str, hashed_password: str) -> bool:
        """일반 패스워드와 해싱한 패스워드가 일치하는지 비교한 후 True/False 반환"""
        return pw_context.verify(plain_password, hashed_password)  # type:ignore


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(seconds=TOKEN_EXPIRE_SECONDS)
    to_encode.update({JWT_EXPIRE_KEY: expire})
    token = jwt.encode(to_encode, JWT_SECRET_KEY, JWT_ALGORITHM)
    return token  # type:ignore


# ! token에 oauth2_scheme 의존성 주입
def authenticate(
    token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)
) -> User:
    """Token / User Validate"""
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail=CREDENTIALS_VALIDATE_FAILED,
        headers={"WWW-Authenticate": TOKEN_TYPE},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, JWT_ALGORITHM)
        user_email: str = payload.get(JWT_SUBJECT_KEY)
        if user_email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = session.exec(select(User).where(User.email == user_email)).first()
    if user is None:
        raise credentials_exception
    if user.disabled:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail=INACTVE_USER)
    return user

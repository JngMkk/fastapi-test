from pydantic import BaseModel, EmailStr
from sqlalchemy.dialects.mysql import INTEGER
from sqlmodel import Column, Field, Relationship, SQLModel

from common.models import TimeStampModel
from core.settings import PW_PATTERN, TOKEN_TYPE


class UserBase(SQLModel):
    """User Base Model"""

    id: int = Field(
        default=None,
        sa_column=Column(INTEGER(unsigned=True), primary_key=True),
        primary_key=True,
    )
    email: EmailStr = Field(..., unique=True, index=True, description="유저 Email")


# * Table True -> app start될 때 테이블 만듦 (테이블 없을 때만)
class User(UserBase, TimeStampModel, table=True):
    """User Table"""

    __tablename__ = "users"

    password: str = Field(..., description="비밀번호")
    disabled: bool = Field(default=False, description="유저 status")

    events: list["Event"] | None = Relationship(back_populates="user")  # type:ignore


class ReadUser(UserBase):
    """조회 Serializer"""

    class Config:
        schema_extra = {"example": {"id": 1, "email": "example1@example.com"}}


class SignUpUser(BaseModel):
    """회원가입 Serializer"""

    email: EmailStr = Field(..., unique=True, index=True, description="유저 Email")
    password: str = Field(..., regex=PW_PATTERN, description="비밀번호")

    class Config:
        schema_extra = {"example": {"email": "example1@example.com", "password": "Example1!"}}


class TokenResponse(BaseModel):
    """Token 반환 Serializer"""

    access_token: str
    token_type: str = TOKEN_TYPE

    class Config:
        schema_extra = {"example": {"access_token": "JWT Access Token", "token_type": TOKEN_TYPE}}

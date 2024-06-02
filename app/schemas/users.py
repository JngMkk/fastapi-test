from dataclasses import dataclass
from datetime import datetime
from typing import Any

from pydantic import UUID4, BaseModel, EmailStr, Field, model_serializer, model_validator
from typing_extensions import Self

from app.config import settings
from app.exceptions import UnProcessableException
from app.handlers.auth import PasswordHandler


@dataclass
class SignInData:
    email: str
    password: str


class SignInSchema(BaseModel):
    email: EmailStr = Field(..., description="user email")
    password: str = Field(..., min_length=8, max_length=20, description="user password")


class SignUpSchema(SignInSchema):
    password2: str = Field(..., min_length=8, max_length=20, description="user password")

    @model_validator(mode="after")
    def validate_password(self) -> Self:
        pwd1 = self.password
        pwd2 = self.password2
        if pwd1 != pwd2:
            raise UnProcessableException("Password not matched.")
        if not PasswordHandler.validate_password(pwd1):
            raise UnProcessableException("Invalid Password.")
        return self

    @model_serializer
    def serialize(self) -> dict[str, Any]:
        self.__dict__.pop("password2")
        return self.__dict__


class ReadUserSchema(BaseModel):
    id: UUID4
    email: str
    created_at: datetime


class JWTSchema(BaseModel):
    access_token: str
    token_type: str = settings.TOKEN_TYPE

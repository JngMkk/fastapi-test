from typing import Any

from fastapi import HTTPException


class CustomException(HTTPException):
    detail: Any
    status_code: int
    headers: dict[str, str] | None = None

    def __init__(
        self, detail: Any = None, headers: dict[str, str] = {"Content-Type": "application/json"}
    ) -> None:
        super().__init__(self.status_code, detail or self.detail, headers or self.headers)


class SignInException(CustomException):
    detail = "Email not existed or password not matched."
    status_code = 401


class UnAuthorizedException(CustomException):
    detail = "UnAuthorized Request."
    status_code = 401
    headers = {"WWW-Authenticate": "Bearer"}


class InvalidTokenException(CustomException):
    detail = "Invalid Token."
    status_code = 401


class ForbiddenException(CustomException):
    detail = "Access Forbidden."
    status_code = 403


class NotFoundException(CustomException):
    detail = "Resource Not Found."
    status_code = 404


class ConflictException(CustomException):
    detail = "Resource Already Exists."
    status_code = 409


class UnProcessableException(CustomException):
    detail = "Invalid Input."
    status_code = 422


class ServiceUnavailableException(CustomException):
    detail = "There was a problem processing your request, please try again later."
    status_code = 503

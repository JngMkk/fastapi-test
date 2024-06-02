from fastapi import APIRouter, Request, Response
from pydantic_core import ValidationError

from app.deps import CURR_USER, DB_SESSION, REDIS
from app.exceptions import NotFoundException, SignInException
from app.handlers.auth import PasswordHandler
from app.handlers.jwt import TokenIssuer
from app.models.users import User
from app.schemas.users import JWTSchema, ReadUserSchema, SignInData, SignInSchema, SignUpSchema

users_router = APIRouter(prefix="/users", tags=["users"])


@users_router.post("/signup", summary="회원 가입", status_code=201, response_model=ReadUserSchema)
async def sign_up(body: SignUpSchema, db: DB_SESSION) -> User:
    user = User(**body.model_dump())
    user.password = PasswordHandler.hash_password(user.password)
    return await User.create(db, user)


@users_router.post("/signin", summary="로그인", status_code=200)
async def sign_in(
    request: Request,
    response: Response,
    body: SignInData,
    db: DB_SESSION,
    redis: REDIS,
) -> JWTSchema:
    try:
        user_body = SignInSchema(email=body.email, password=body.password)
        user = await User.get(db, [User.email == user_body.email])
        if not PasswordHandler.verify_password(body.password, user.password):
            raise SignInException

        issuer = TokenIssuer(request, response, redis)
        return JWTSchema(access_token=await issuer.issue_token(user))
    except (ValidationError, NotFoundException):
        raise SignInException


@users_router.post("/signout", summary="로그아웃", status_code=200)
async def sign_out(request: Request, response: Response, user: CURR_USER, redis: REDIS) -> None:
    issuer = TokenIssuer(request, response, redis)
    await issuer.revoke_token()
    return None


@users_router.post("/refresh", summary="액세스 토큰 재발급", status_code=200)
async def refresh_token(request: Request, response: Response, redis: REDIS) -> JWTSchema:
    """### Cookie에 Refresh Token 없을 경우 InvalidTokenException"""

    issuer = TokenIssuer(request, response, redis)
    return JWTSchema(access_token=await issuer.rotate_token())

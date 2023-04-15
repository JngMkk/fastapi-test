from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT

from common.consts import CURR_USER, SESSION
from core.auth import HashPassWord, create_access_token
from core.settings import JWT_SUBJECT_KEY

from .constant.errors import USER_ALREADY_EXISTS, WRONG_CREDENTIAL
from .models import ReadUser, SignUpUser, TokenResponse, User

user_router = APIRouter(tags=["Users"])
hash_password = HashPassWord()


# * response_model=ReadUser 지정하면 ReadUser로 Auto JSON Serialize
@user_router.post("/signup", status_code=HTTP_201_CREATED, response_model=ReadUser)
async def create_user(form: SignUpUser, session: Session = SESSION) -> User:
    query = select(User).where(User.email == form.email)
    user = session.exec(query).first()
    if user is not None:
        raise HTTPException(status_code=HTTP_409_CONFLICT, detail=USER_ALREADY_EXISTS)

    hashed_pw = hash_password.create_hash(form.password)
    form.password = hashed_pw

    user = User.from_orm(form)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# * OAuth2PasswordRequestForm: FastAPI에서 제공하는 Login Form
# * Depends 함수를 통해 의존성을 주입하여 OAuth2 사양을 엄격하게 따르도록 함.
@user_router.post("/signin", status_code=HTTP_200_OK, response_model=TokenResponse)
async def login_user(
    form: OAuth2PasswordRequestForm = Depends(), session: Session = SESSION
) -> TokenResponse:
    """User 존재 유무 검사 및 Token 생성"""
    query = select(User).where(User.email == form.username)
    user = session.exec(query).first()
    if user is None or not hash_password.check_password(form.password, user.password):
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail=WRONG_CREDENTIAL)

    access_token = create_access_token(data={JWT_SUBJECT_KEY: user.email})
    return TokenResponse(access_token=access_token)


@user_router.get("/me", status_code=HTTP_200_OK, response_model=ReadUser)
async def get_curr_user(user: User = CURR_USER) -> User:
    """Token 및 User 유효성 검사 후 User 반환"""
    return user

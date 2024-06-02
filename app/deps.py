from typing import Annotated

from aioredis import Redis
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .handlers.auth import AuthHandler
from .handlers.db import get_db_session
from .handlers.redis import get_redis
from .models.users import User

DB_SESSION = Annotated[AsyncSession, Depends(get_db_session)]

REDIS = Annotated[Redis, Depends(get_redis)]

CURR_USER = Annotated[User, Depends(AuthHandler.get_curr_user)]

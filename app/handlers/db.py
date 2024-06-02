from typing import AsyncGenerator

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import settings
from app.models.base import ModelBase

ENGINE = create_async_engine(
    settings.MYSQL_URL,
    future=True,
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
)
SESSION = async_sessionmaker(bind=ENGINE, autocommit=False, expire_on_commit=False)


async def get_db_session() -> AsyncGenerator:
    async with SESSION() as sess:
        try:
            yield sess
        except SQLAlchemyError:
            await sess.rollback()


async def create_all_tables() -> None:
    async with ENGINE.begin() as conn:
        # await conn.run_sync(ModelBase.metadata.drop_all)
        await conn.run_sync(ModelBase.metadata.create_all)
    await ENGINE.dispose()

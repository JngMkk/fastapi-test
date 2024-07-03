import pytest
from aioredis import from_url
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.apis.events import event_router
from app.apis.users import users_router
from app.config import get_settings
from app.models.base import ModelBase

settings = get_settings(".test.env")
engine = create_async_engine(settings.MYSQL_URL)
async_session = async_sessionmaker(bind=engine, autocommit=False, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
async def start_db():
    async with engine.begin() as conn:
        await conn.run_sync(ModelBase.metadata.drop_all)
        await conn.run_sync(ModelBase.metadata.create_all)
    await engine.dispose()


@pytest.fixture(scope="session")
def app():
    _app = FastAPI(root_path="/api/v1")
    _app.include_router(event_router)
    _app.include_router(users_router)
    return _app


@pytest.fixture(scope="session")
async def db(start_db):
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.rollback()


@pytest.fixture(scope="session")
async def redis():
    async with from_url(settings.REDIS_URL) as r:
        await r.flushall()
        yield r
        await r.close()


@pytest.fixture(scope="session")
async def client(app):
    transport = ASGITransport(app=app, root_path="/api/v1")
    async with AsyncClient(base_url="http://test", transport=transport) as ac:
        yield ac
        await ac.aclose()


@pytest.fixture(
    scope="session",
    params=[pytest.param(("asyncio", {"use_uvloop": True}), id="asynciopytest")],
)
def anyio_backend(request):
    return request.param

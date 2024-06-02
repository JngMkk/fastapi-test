from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware

from .apis.events import event_router
from .apis.users import users_router
from .handlers.db import create_all_tables


def init_app() -> FastAPI:
    @asynccontextmanager
    async def lifspan(app: FastAPI):
        await create_all_tables()
        yield

    app = FastAPI(
        title="Payhere Backend",
        description="Payhere backend APIs",
        version="v1",
        root_path="/api/v1",
        lifespan=lifspan,
        middleware=[
            Middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        ],
    )
    app.include_router(event_router)
    app.include_router(users_router)
    return app


app = init_app()

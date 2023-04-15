import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.planners.routes import event_router
from apps.users.routes import user_router
from core.database import conn

app = FastAPI()

app.include_router(user_router, prefix="/users")
app.include_router(event_router, prefix="/events")


@app.on_event("startup")
def on_startup() -> None:
    conn()


# * CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)

from fastapi import APIRouter, Path, Query

from app.deps import CURR_USER, DB_SESSION
from app.models.events import Event
from app.schemas.events import CreateEventSchema, ReadEventSchema, UpdateEventSchema

event_router = APIRouter(prefix="/events", tags=["Events"])


@event_router.post("", status_code=201, response_model=ReadEventSchema)
async def create_event(body: CreateEventSchema, user: CURR_USER, db: DB_SESSION):
    event = Event(**body.model_dump(), user_id=user.id)
    return await Event.create(db, event)


@event_router.get("", status_code=200, response_model=list[ReadEventSchema])
async def list_events(
    user: CURR_USER, db: DB_SESSION, offset: int = 0, limit: int = Query(default=20)
):
    return await Event.list(db, [Event.user_id == user.id], offset, limit)


@event_router.get("/{id}", status_code=200, response_model=ReadEventSchema)
async def detail_event(user: CURR_USER, db: DB_SESSION, id: int = Path(..., ge=1)):
    return await Event.get(db, [Event.id == id, Event.user_id == user.id])


@event_router.put("/{id}", status_code=200, response_model=ReadEventSchema)
async def update_event(
    body: UpdateEventSchema, user: CURR_USER, db: DB_SESSION, id: int = Path(..., ge=1)
):
    event = await Event.get(db, [Event.id == id, Event.user_id == user.id])
    return await Event.update(db, event, **body.model_dump(exclude_unset=True))


@event_router.delete("/{id}", status_code=204)
async def delete_event(user: CURR_USER, db: DB_SESSION, id: int = Path(..., ge=1)):
    return await Event.delete(db, [Event.id == id, Event.user_id == user.id])

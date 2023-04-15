from fastapi import APIRouter, Body, HTTPException, Query
from sqlmodel import Session, func, select, update
from sqlmodel.sql.expression import SelectOfScalar
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)

from apps.users.models import User
from common.consts import CURR_USER, SESSION

from .constant.errors import EVENT_NOT_FOUND, NUMBER_EVENTS_EXCEEDED
from .constant.params import SEQ_PATH
from .models import CreateEvent, Event, ReadEvent, UpdateEvent

event_router = APIRouter(tags=["Events"])


def select_event_by_user(user: User) -> SelectOfScalar[Event]:
    return select(Event).where(Event.user_id == user.id)


@event_router.post("/", status_code=HTTP_201_CREATED, response_model=ReadEvent)
async def create_event(
    user: User = CURR_USER, body: CreateEvent = Body(...), session: Session = SESSION
) -> Event:
    """이벤트 생성"""
    existing_events_cnt: int = session.exec(  # type:ignore
        select([func.count(Event.id)]).where(Event.user_id == user.id)
    ).one()

    if existing_events_cnt >= 20:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=NUMBER_EVENTS_EXCEEDED)

    event = Event.from_orm(body, update={"user_id": user.id, "seq": existing_events_cnt + 1})
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


@event_router.get("/", status_code=HTTP_200_OK, response_model=list[ReadEvent])
async def list_events(
    user: User = CURR_USER,
    session: Session = SESSION,
    offset: int = 0,
    limit: int = Query(default=20, lte=20),
) -> list[Event]:
    """해당 유저 이벤트 전체 검색"""
    query = select_event_by_user(user).offset(offset).limit(limit)
    events = session.exec(query).all()
    return events


@event_router.delete("/", status_code=HTTP_204_NO_CONTENT)
async def delete_events(user: User = CURR_USER, session: Session = SESSION) -> None:
    """이벤트 전체 삭제"""
    session.query(Event).filter_by(user_id=user.id).delete()
    session.commit()
    return


@event_router.get("/{seq}", status_code=HTTP_200_OK, response_model=ReadEvent)
async def detail_event(
    seq: int = SEQ_PATH, user: User = CURR_USER, session: Session = SESSION
) -> Event:
    """해당 번호 유저 이벤트 조회"""
    query = select_event_by_user(user).where(Event.seq == seq)
    event = session.exec(query).first()
    if event is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=EVENT_NOT_FOUND)
    return event


@event_router.patch("/{seq}", status_code=HTTP_200_OK, response_model=ReadEvent)
async def update_event(
    seq: int = SEQ_PATH,
    user: User = CURR_USER,
    body: UpdateEvent = Body(...),
    session: Session = SESSION,
) -> Event:
    """해당 이벤트 수정"""
    query = select_event_by_user(user).where(Event.seq == seq)
    event = session.exec(query).first()
    if event is not None:
        data = body.dict(exclude_unset=True)
        for k, v in data.items():
            setattr(event, k, v)
        session.add(event)
        session.commit()
        session.refresh(event)

        return event

    raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=EVENT_NOT_FOUND)


@event_router.delete("/{seq}", status_code=HTTP_204_NO_CONTENT)
async def delete_event(
    user: User = CURR_USER, seq: int = SEQ_PATH, session: Session = SESSION
) -> None:
    """해당 번호 이벤트 삭제"""
    event = session.exec(select_event_by_user(user).where(Event.seq == seq)).first()
    if event is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=EVENT_NOT_FOUND)

    delete_seq = event.seq
    session.delete(event)
    session.commit()

    query = (
        update(Event)
        .where(Event.user_id == user.id, Event.seq > delete_seq)
        .values(seq=Event.seq - 1)
    )
    session.exec(query)  # type:ignore
    session.commit()
    return

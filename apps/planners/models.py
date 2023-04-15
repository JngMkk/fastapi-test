from typing import Optional

from sqlalchemy.dialects.mysql import INTEGER, TINYINT
from sqlmodel import JSON, CheckConstraint, Column, Field, ForeignKey, Relationship, SQLModel

from common.models import TimeStampModel


class EventBase(SQLModel):
    """Event Model Base"""

    title: str = Field(..., max_length=30, description="이벤트 제목")
    description: str = Field(default=None, max_length=100, description="이벤트 설명")
    tags: list[str] = Field(..., sa_column=Column(JSON, nullable=False), description="이벤트 태그")
    image: str = Field(default=None, max_length=255, description="이벤트 썸네일 이미지")
    location: str = Field(..., max_length=50, description="이벤트 장소")

    class Config:
        schema_extra = {
            "example": {
                "title": "Go to SeokChon Lake",
                "image": "https://i.ytimg.com/vi/25LZxd6Oamk/maxresdefault.jpg",
                "description": "Go to SeokChon Lake with girlfriend (Dream comes true!)",
                "tags": ["travel", "date"],
                "location": "Seokchon Lake, Seoul",
            }
        }


class Event(EventBase, TimeStampModel, table=True):
    """Event Table"""

    __tablename__ = "events"
    __table_args__ = (CheckConstraint("seq <= 20", name="check_seq_le_20"),)

    id: int = Field(
        default=None,
        sa_column=Column(INTEGER(unsigned=True), primary_key=True),
        primary_key=True,
        description="이벤트 ID",
    )
    seq: int = Field(
        default=None, le=20, sa_column=Column(TINYINT, nullable=False), description="회원 별 evnet seq"
    )
    user_id: int = Field(
        default=None,
        sa_column=Column(INTEGER(unsigned=True), ForeignKey("users.id"), nullable=False),
        foreign_key="users.id",
        description="유저 ID",
    )

    user: Optional["User"] = Relationship(back_populates="events")  # type:ignore


class ReadEvent(EventBase):
    """Event 조회"""

    seq: int

    class Config:
        schema_extra = {
            "example": {
                "seq": 1,
                "title": "Go to SeokChon Lake",
                "image": "https://i.ytimg.com/vi/25LZxd6Oamk/maxresdefault.jpg",
                "description": "Go to SeokChon Lake with girlfriend (Dream comes true!)",
                "tags": ["travel", "date"],
                "location": "Seokchon Lake, Seoul",
            }
        }


class CreateEvent(EventBase):
    """Event 생성"""

    pass


class UpdateEvent(SQLModel):
    """Event 변경"""

    title: str | None
    description: str | None
    tags: list[str] | None
    image: str | None
    location: str | None

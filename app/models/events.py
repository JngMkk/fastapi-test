from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, ForeignKeyConstraint, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import ModelBase

if TYPE_CHECKING:
    from .users import User


class Event(ModelBase):
    __tablename__ = "events"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="events_pkey"),
        ForeignKeyConstraint(
            ["user_id"], ["testdb.users.id"], ondelete="CASCADE", name="users_id_fkey"
        ),
        {"schema": "testdb"},
    )

    id: Mapped[int] = mapped_column(primary_key=True, doc="event id")
    title: Mapped[str] = mapped_column(String(30), doc="event title")
    description: Mapped[str] = mapped_column(String(100), nullable=True, doc="event description")
    tags: Mapped[list[str]] = mapped_column(JSON(), nullable=True, doc="event tags")
    image: Mapped[str] = mapped_column(String(255), nullable=True, doc="evevnt thumbnail image")
    location: Mapped[str] = mapped_column(String(50), nullable=True, doc="event location")
    is_checked: Mapped[bool] = mapped_column(Boolean(), default=0)
    user_id: Mapped[str] = mapped_column(String(36))

    user: Mapped["User"] = relationship("User", back_populates="events")

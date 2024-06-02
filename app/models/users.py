from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, PrimaryKeyConstraint, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import ModelBase

if TYPE_CHECKING:
    from .events import Event


class User(ModelBase):
    __tablename__ = "users"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="users_pkey"),
        UniqueConstraint("email", name="users_eamil_ukey"),
        {"schema": "testdb"},
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid4, doc="user uuid")
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, doc="user email")
    password: Mapped[str] = mapped_column(String(60), doc="hashed password")
    is_disabled: Mapped[bool] = mapped_column(Boolean(), default=0, doc="is disabled?")
    is_admin: Mapped[bool] = mapped_column(Boolean(), default=0, doc="is admin?")

    events: Mapped[list["Event"]] = relationship("Event", back_populates="user")

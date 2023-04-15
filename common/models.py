from datetime import datetime

from sqlmodel import Field, SQLModel


class TimeStampModel(SQLModel):
    created_at: datetime = Field(default=datetime.now(), nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now)

from pydantic import BaseModel, Field


class EventBassSchema(BaseModel):
    title: str = Field(..., max_length=30)
    description: str | None = Field(default=None, max_length=100)
    tags: list[str] | None = Field(default=None)
    image: str | None = Field(default=None, max_length=255)
    location: str | None = Field(default=None, max_length=50)


class ReadEventSchema(EventBassSchema):
    id: int
    is_checked: bool


class CreateEventSchema(EventBassSchema):
    pass


class UpdateEventSchema(EventBassSchema):
    title: str = Field(default=None)
    is_checked: bool = Field(default=None)

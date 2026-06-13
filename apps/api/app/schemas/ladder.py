import uuid
from datetime import datetime

from pydantic import BaseModel


class LadderEntry(BaseModel):
    rank: int
    user_id: uuid.UUID | None
    user_login: str
    user_display_name: str | None
    message_count: int
    videos_count: int
    first_message_at: datetime | None
    last_message_at: datetime | None


class LadderRead(BaseModel):
    channel_id: uuid.UUID
    videos_count: int
    total_messages: int
    unique_chatters: int
    items: list[LadderEntry]

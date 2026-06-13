import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChannelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    twitch_id: str | None
    login: str
    display_name: str | None
    avatar_url: str | None
    twitch_created_at: datetime | None
    fetched_at: datetime | None


class ChannelSummary(BaseModel):
    channel: ChannelRead
    videos_count: int
    scanned_videos_count: int
    total_messages: int
    unique_chatters: int

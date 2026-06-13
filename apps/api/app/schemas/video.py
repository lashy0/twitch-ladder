import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.shared.enums import VideoChatScanStatus


class VideoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    twitch_video_id: str
    channel_id: uuid.UUID
    title: str
    duration_seconds: int | None
    published_at: datetime | None
    view_count: int | None
    thumbnail_url: str | None
    chat_scan_status: VideoChatScanStatus
    fetched_at: datetime | None


class VideoList(BaseModel):
    items: list[VideoRead]
    total: int

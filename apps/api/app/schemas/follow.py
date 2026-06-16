from datetime import datetime

from pydantic import BaseModel

from app.schemas.channel import ChannelRead


class FollowRead(BaseModel):
    twitch_id: str
    login: str
    display_name: str
    avatar_url: str | None
    followed_at: datetime | None
    twitch_created_at: datetime | None
    language: str


class FollowRegionRead(BaseModel):
    language: str
    count: int
    percent: float


class FollowList(BaseModel):
    channel: ChannelRead
    items: list[FollowRead]
    total: int
    followers_total: int | None
    regions: list[FollowRegionRead]
    next_cursor: str | None

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel

from app.schemas.channel import ChannelRead


class RoleCategory(StrEnum):
    MODS = "mods"
    VIPS = "vips"
    FOUNDERS = "founders"
    ARTISTS = "artists"


class RoleRead(BaseModel):
    twitch_id: str
    login: str
    display_name: str
    avatar_url: str | None
    category: RoleCategory
    granted_at: datetime | None
    twitch_created_at: datetime | None


class RoleStatRead(BaseModel):
    category: RoleCategory
    count: int
    percent: float


class RoleList(BaseModel):
    channel: ChannelRead
    items: list[RoleRead]
    total: int
    followers_total: int | None
    follows_total: int | None
    stats: list[RoleStatRead]

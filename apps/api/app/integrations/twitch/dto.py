from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class TwitchUserData:
    """Normalized Twitch user data returned by an integration client."""

    twitch_id: str
    login: str
    display_name: str
    avatar_url: str | None
    created_at: datetime | None


@dataclass(frozen=True, slots=True)
class TwitchVideoData:
    """Normalized Twitch VOD data returned by an integration client."""

    twitch_video_id: str
    channel_twitch_id: str
    title: str
    duration_seconds: int | None
    published_at: datetime | None
    view_count: int | None
    thumbnail_url: str | None


@dataclass(frozen=True, slots=True)
class TwitchVideoPage:
    """One page of Twitch VOD data."""

    items: list[TwitchVideoData]
    cursor: str | None

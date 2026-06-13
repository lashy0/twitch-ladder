import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import TwitchUser
from app.repositories import (
    TwitchUserRepository,
    VideoChatterRepository,
    VideoRepository,
)
from app.shared.enums import VideoChatScanStatus


class ChannelService:
    """Use cases for local Twitch channel projections."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the service.

        Args:
            session: Active SQLAlchemy async session.
        """
        self._users = TwitchUserRepository(session)
        self._videos = VideoRepository(session)
        self._chatters = VideoChatterRepository(session)

    async def get_by_login(self, login: str) -> TwitchUser | None:
        """Return a channel by Twitch login.

        Args:
            login: Twitch login. The lookup is normalized by the repository.

        Returns:
            Matching channel, or `None` when it does not exist locally.
        """
        return await self._users.get_by_login(login)

    async def get_by_id(self, channel_id: uuid.UUID) -> TwitchUser | None:
        """Return a channel by local database ID.

        Args:
            channel_id: Local `twitch_users.id`.

        Returns:
            Matching channel, or `None` when it does not exist locally.
        """
        return await self._users.get_by_id(channel_id)

    async def upsert_channel(
        self,
        *,
        login: str,
        twitch_id: str | None = None,
        display_name: str | None = None,
        avatar_url: str | None = None,
        twitch_created_at: datetime | None = None,
        fetched_at: datetime | None = None,
    ) -> TwitchUser:
        """Create or refresh a local channel projection.

        Args:
            login: Twitch login.
            twitch_id: External Twitch user ID when known.
            display_name: Twitch display name for UI.
            avatar_url: Twitch avatar URL for UI.
            twitch_created_at: Twitch account creation time.
            fetched_at: Time when the Twitch data was fetched.

        Returns:
            Created or updated channel.
        """
        return await self._users.upsert(
            login=login,
            twitch_id=twitch_id,
            display_name=display_name,
            avatar_url=avatar_url,
            twitch_created_at=twitch_created_at,
            fetched_at=fetched_at,
        )

    async def get_summary_counts(self, channel_id: uuid.UUID) -> tuple[int, int, int, int]:
        """Return basic aggregate counts for a channel.

        Args:
            channel_id: Local `twitch_users.id`.

        Returns:
            Tuple of `videos_count`, `scanned_videos_count`, `total_messages`,
            and `unique_chatters`.
        """
        videos_count = await self._videos.count_by_channel(channel_id)
        scanned_videos_count = await self._videos.count_by_channel(
            channel_id,
            chat_scan_status=VideoChatScanStatus.COMPLETED,
        )
        total_messages = await self._chatters.sum_messages_by_channel(channel_id)
        unique_chatters = await self._chatters.count_unique_chatters_by_channel(channel_id)
        return videos_count, scanned_videos_count, total_messages, unique_chatters

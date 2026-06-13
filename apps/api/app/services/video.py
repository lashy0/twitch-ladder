import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Video
from app.repositories import VideoRepository
from app.shared.enums import VideoChatScanStatus


class VideoService:
    """Use cases for local Twitch VOD projections."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the service.

        Args:
            session: Active SQLAlchemy async session.
        """
        self._videos = VideoRepository(session)

    async def get_by_id(self, video_id: uuid.UUID) -> Video | None:
        """Return a VOD by local database ID.

        Args:
            video_id: Local `videos.id`.

        Returns:
            Matching video, or `None` when it does not exist locally.
        """
        return await self._videos.get_by_id(video_id)

    async def list_by_channel(
        self,
        channel_id: uuid.UUID,
        *,
        limit: int = 40,
        offset: int = 0,
    ) -> list[Video]:
        """Return VODs for a channel.

        Args:
            channel_id: Local `twitch_users.id` of the channel.
            limit: Maximum number of VODs.
            offset: Number of VODs to skip.

        Returns:
            VODs ordered by publish time.
        """
        return await self._videos.list_by_channel(
            channel_id,
            limit=limit,
            offset=offset,
        )

    async def count_by_channel(self, channel_id: uuid.UUID) -> int:
        """Return number of VODs for a channel.

        Args:
            channel_id: Local `twitch_users.id` of the channel.

        Returns:
            Number of local VOD projections for the channel.
        """
        return await self._videos.count_by_channel(channel_id)

    async def upsert_video(
        self,
        *,
        twitch_video_id: str,
        channel_id: uuid.UUID,
        title: str,
        duration_seconds: int | None = None,
        published_at: datetime | None = None,
        view_count: int | None = None,
        thumbnail_url: str | None = None,
        chat_scan_status: VideoChatScanStatus | None = None,
        fetched_at: datetime | None = None,
    ) -> Video:
        """Create or refresh a local VOD projection.

        Args:
            twitch_video_id: External Twitch VOD ID.
            channel_id: Local channel owner ID.
            title: VOD title.
            duration_seconds: VOD duration in seconds.
            published_at: Twitch publish time.
            view_count: Twitch view count.
            thumbnail_url: VOD preview image URL.
            chat_scan_status: Optional chat scan status override.
            fetched_at: Time when the Twitch data was fetched.

        Returns:
            Created or updated VOD.
        """
        return await self._videos.upsert(
            twitch_video_id=twitch_video_id,
            channel_id=channel_id,
            title=title,
            duration_seconds=duration_seconds,
            published_at=published_at,
            view_count=view_count,
            thumbnail_url=thumbnail_url,
            chat_scan_status=chat_scan_status,
            fetched_at=fetched_at,
        )

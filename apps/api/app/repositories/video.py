import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Video
from app.shared.enums import VideoChatScanStatus


class VideoRepository:
    """Database access for Twitch VOD projections."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository.

        Args:
            session: Active SQLAlchemy async session.
        """
        self._session = session

    async def get_by_id(self, video_id: uuid.UUID) -> Video | None:
        """Return a VOD by local database ID.

        Args:
            video_id: Local `videos.id`.

        Returns:
            Matching video, or `None` when it does not exist.
        """
        return await self._session.get(Video, video_id)

    async def get_by_twitch_video_id(self, twitch_video_id: str) -> Video | None:
        """Return a VOD by Twitch video ID.

        Args:
            twitch_video_id: External Twitch VOD ID.

        Returns:
            Matching video, or `None` when it does not exist.
        """
        stmt = select(Video).where(Video.twitch_video_id == twitch_video_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_channel(
        self,
        channel_id: uuid.UUID,
        *,
        limit: int = 40,
        offset: int = 0,
    ) -> list[Video]:
        """Return VODs for a channel ordered by publish time.

        Args:
            channel_id: Local `twitch_users.id` of the channel.
            limit: Maximum number of rows to return.
            offset: Number of rows to skip.

        Returns:
            List of videos for the channel.
        """
        stmt = (
            select(Video)
            .where(Video.channel_id == channel_id)
            .order_by(Video.published_at.desc().nulls_last(), Video.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_channel(
        self,
        channel_id: uuid.UUID,
        *,
        chat_scan_status: VideoChatScanStatus | None = None,
    ) -> int:
        """Return number of VODs for a channel.

        Args:
            channel_id: Local `twitch_users.id` of the channel.
            chat_scan_status: Optional chat scan status filter.

        Returns:
            Number of matching VODs.
        """
        stmt = select(func.count(Video.id)).where(Video.channel_id == channel_id)
        if chat_scan_status is not None:
            stmt = stmt.where(Video.chat_scan_status == chat_scan_status)

        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def upsert(
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
        """Create or update a local Twitch VOD projection.

        Args:
            twitch_video_id: External Twitch VOD ID.
            channel_id: Local channel owner ID.
            title: VOD title.
            duration_seconds: VOD duration in seconds.
            published_at: Twitch publish time.
            view_count: Twitch view count.
            thumbnail_url: VOD preview image URL.
            chat_scan_status: Optional chat scan status override.
            fetched_at: Time when this projection was refreshed from Twitch.

        Returns:
            Created or updated video.
        """
        video = await self.get_by_twitch_video_id(twitch_video_id)
        if video is None:
            video = Video(
                twitch_video_id=twitch_video_id,
                channel_id=channel_id,
                title=title,
            )
            self._session.add(video)

        video.channel_id = channel_id
        video.title = title
        video.duration_seconds = duration_seconds
        video.published_at = published_at
        video.view_count = view_count
        video.thumbnail_url = thumbnail_url
        video.fetched_at = fetched_at
        if chat_scan_status is not None:
            video.chat_scan_status = chat_scan_status

        await self._session.flush()
        return video

    async def update_chat_scan_status(
        self,
        video_id: uuid.UUID,
        status: VideoChatScanStatus,
    ) -> Video | None:
        """Update the chat scan status for a VOD.

        Args:
            video_id: Local `videos.id`.
            status: New chat scan status.

        Returns:
            Updated video, or `None` when it does not exist.
        """
        video = await self.get_by_id(video_id)
        if video is None:
            return None

        video.chat_scan_status = status
        await self._session.flush()
        return video

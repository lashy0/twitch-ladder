import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts import LadderResult
from app.repositories import VideoChatterRepository, VideoRepository


class LadderService:
    """Use cases for channel ladder read models."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the service.

        Args:
            session: Active SQLAlchemy async session.
        """
        self._chatters = VideoChatterRepository(session)
        self._videos = VideoRepository(session)

    async def get_by_channel(
        self,
        channel_id: uuid.UUID,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> LadderResult:
        """Return an aggregated ladder for a channel.

        Args:
            channel_id: Local `twitch_users.id` of the channel.
            limit: Maximum number of ladder rows.
            offset: Number of ladder rows to skip.

        Returns:
            Ladder result with rows and summary counters.
        """
        rows = await self._chatters.get_ladder_by_channel(
            channel_id=channel_id,
            limit=limit,
            offset=offset,
        )
        videos_count = await self._videos.count_by_channel(channel_id)
        total_messages = await self._chatters.sum_messages_by_channel(channel_id)
        unique_chatters = await self._chatters.count_unique_chatters_by_channel(channel_id)

        return LadderResult(
            channel_id=channel_id,
            videos_count=videos_count,
            total_messages=total_messages,
            unique_chatters=unique_chatters,
            rows=rows,
        )

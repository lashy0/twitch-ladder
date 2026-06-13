import uuid
from datetime import datetime

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts import LadderRow, VideoChatterAggregate
from app.models import Video, VideoChatter


class VideoChatterRepository:
    """Database access for per-VOD chat activity aggregates."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository.

        Args:
            session: Active SQLAlchemy async session.
        """
        self._session = session

    async def get_by_video_and_login(
        self,
        *,
        video_id: uuid.UUID,
        user_login: str,
    ) -> VideoChatter | None:
        """Return a chatter aggregate by VOD and login.

        Args:
            video_id: Local `videos.id`.
            user_login: Twitch login. The lookup is normalized to lowercase.

        Returns:
            Matching aggregate, or `None` when it does not exist.
        """
        stmt = select(VideoChatter).where(
            VideoChatter.video_id == video_id,
            VideoChatter.user_login == user_login.lower(),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert_aggregates(
        self,
        *,
        video_id: uuid.UUID,
        aggregates: list[VideoChatterAggregate],
    ) -> list[VideoChatter]:
        """Create or update chatter aggregates for one VOD.

        Args:
            video_id: Local VOD ID these aggregates belong to.
            aggregates: Per-user aggregate input rows.

        Returns:
            Created or updated ORM rows.
        """
        rows: list[VideoChatter] = []
        for aggregate in aggregates:
            user_login = aggregate.user_login.lower()
            row = await self.get_by_video_and_login(
                video_id=video_id,
                user_login=user_login,
            )
            if row is None:
                row = VideoChatter(video_id=video_id, user_login=user_login)
                self._session.add(row)

            row.user_id = aggregate.user_id
            row.user_display_name = aggregate.user_display_name
            row.message_count = aggregate.message_count
            row.first_message_at = aggregate.first_message_at
            row.last_message_at = aggregate.last_message_at
            rows.append(row)

        await self._session.flush()
        return rows

    async def get_ladder_by_channel(
        self,
        *,
        channel_id: uuid.UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[LadderRow]:
        """Return channel ladder rows aggregated across channel VODs.

        Args:
            channel_id: Local `twitch_users.id` of the channel.
            limit: Maximum number of rows to return.
            offset: Number of rows to skip.

        Returns:
            Ladder rows ordered by descending message count.
        """
        stmt: Select[tuple[uuid.UUID | None, str, str | None, int, int, datetime | None, datetime | None]] = (
            select(
                VideoChatter.user_id,
                VideoChatter.user_login,
                func.max(VideoChatter.user_display_name),
                func.sum(VideoChatter.message_count),
                func.count(func.distinct(VideoChatter.video_id)),
                func.min(VideoChatter.first_message_at),
                func.max(VideoChatter.last_message_at),
            )
            .join(Video, Video.id == VideoChatter.video_id)
            .where(Video.channel_id == channel_id)
            .group_by(VideoChatter.user_id, VideoChatter.user_login)
            .order_by(func.sum(VideoChatter.message_count).desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return [
            LadderRow(
                user_id=row[0],
                user_login=row[1],
                user_display_name=row[2],
                message_count=row[3],
                videos_count=row[4],
                first_message_at=row[5],
                last_message_at=row[6],
            )
            for row in result.tuples().all()
        ]

    async def count_unique_chatters_by_channel(self, channel_id: uuid.UUID) -> int:
        """Return number of unique chatters across a channel's VODs.

        Args:
            channel_id: Local `twitch_users.id` of the channel.

        Returns:
            Number of unique chatter logins.
        """
        stmt = (
            select(func.count(func.distinct(VideoChatter.user_login)))
            .join(Video, Video.id == VideoChatter.video_id)
            .where(Video.channel_id == channel_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def sum_messages_by_channel(self, channel_id: uuid.UUID) -> int:
        """Return total aggregated chat messages across a channel's VODs.

        Args:
            channel_id: Local `twitch_users.id` of the channel.

        Returns:
            Total message count. Returns zero when no aggregates exist.
        """
        stmt = (
            select(func.coalesce(func.sum(VideoChatter.message_count), 0))
            .join(Video, Video.id == VideoChatter.video_id)
            .where(Video.channel_id == channel_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

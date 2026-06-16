from collections import Counter
from datetime import UTC, datetime

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.twitch import TwitchFollowClient
from app.integrations.twitch.exceptions import TwitchApiError
from app.schemas import ChannelRead, FollowList, FollowRead, FollowRegionRead
from app.services.channel import ChannelService
from app.shared.languages import normalize_language


class FollowService:
    """Fetch and normalize Twitch follow data for the product API."""

    def __init__(
        self,
        session: AsyncSession,
        *,
        follow_client: TwitchFollowClient | None = None,
    ) -> None:
        self._session = session
        self._channels = ChannelService(session)
        self._follow_client = follow_client or TwitchFollowClient()
        self._owns_follow_client = follow_client is None

    async def get(self, login: str, *, limit: int, after: str | None) -> FollowList | None:
        page = await self._follow_client.list_by_login(login, first=limit, after=after)
        region_counts = Counter(normalize_language(item.language) for item in page.items)
        region_total = len(page.items)
        if after is None:
            next_region_cursor = page.cursor
            seen_cursors: set[str] = set()
            while next_region_cursor is not None and next_region_cursor not in seen_cursors:
                seen_cursors.add(next_region_cursor)
                try:
                    region_page = await self._follow_client.list_by_login(
                        login,
                        first=limit,
                        after=next_region_cursor,
                    )
                except TwitchApiError:
                    logger.warning(
                        "Failed to fetch full follow region aggregation login={login}",
                        login=login,
                    )
                    break
                region_counts.update(normalize_language(item.language) for item in region_page.items)
                region_total += len(region_page.items)
                next_region_cursor = region_page.cursor

        owner = page.channel
        now = datetime.now(UTC)
        channel = await self._channels.upsert_channel(
            login=owner.login,
            twitch_id=owner.twitch_id,
            display_name=owner.display_name,
            avatar_url=owner.avatar_url,
            twitch_created_at=owner.created_at,
            fetched_at=now,
        )
        for item in page.items:
            await self._channels.upsert_channel(
                login=item.login,
                twitch_id=item.twitch_id,
                display_name=item.display_name,
                avatar_url=item.avatar_url,
                twitch_created_at=item.created_at,
                fetched_at=now,
            )

        await self._session.commit()
        languages = [normalize_language(item.language) for item in page.items]
        loaded_total = region_total or 1
        return FollowList(
            channel=ChannelRead.model_validate(channel),
            items=[
                FollowRead(
                    twitch_id=item.twitch_id,
                    login=item.login,
                    display_name=item.display_name,
                    avatar_url=item.avatar_url,
                    followed_at=item.followed_at,
                    twitch_created_at=item.created_at,
                    language=language,
                )
                for item, language in zip(page.items, languages, strict=True)
            ],
            total=page.total,
            followers_total=page.followers_total,
            regions=[
                FollowRegionRead(
                    language=language,
                    count=count,
                    percent=round((count / loaded_total) * 100, 1),
                )
                for language, count in region_counts.most_common()
            ],
            next_cursor=page.cursor,
        )

    async def aclose(self) -> None:
        if self._owns_follow_client:
            await self._follow_client.aclose()

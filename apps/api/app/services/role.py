from collections import Counter
from datetime import UTC, datetime
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.twitch import TwitchRoleCategory, TwitchRoleClient, TwitchRolePage
from app.schemas import ChannelRead
from app.schemas.role import RoleCategory, RoleList, RoleRead, RoleStatRead
from app.services.channel import ChannelService

_ROLE_ORDER = [
    RoleCategory.MODS,
    RoleCategory.VIPS,
    RoleCategory.FOUNDERS,
    RoleCategory.ARTISTS,
]


class RoleClient(Protocol):
    async def list_by_login(self, login: str) -> TwitchRolePage: ...

    async def aclose(self) -> None: ...


class RoleService:
    """Fetch and normalize Twitch channel role data for the product API."""

    def __init__(
        self,
        session: AsyncSession,
        *,
        role_client: RoleClient | None = None,
    ) -> None:
        self._session = session
        self._channels = ChannelService(session)
        self._role_client = role_client or TwitchRoleClient()
        self._owns_role_client = role_client is None

    async def get(self, login: str) -> RoleList:
        page = await self._role_client.list_by_login(login)
        now = datetime.now(UTC)

        owner = page.channel
        channel = await self._channels.upsert_channel(
            login=owner.login,
            twitch_id=owner.twitch_id,
            display_name=owner.display_name,
            avatar_url=owner.avatar_url,
            twitch_created_at=owner.created_at,
            fetched_at=now,
        )
        for item in page.items:
            user = item.user
            await self._channels.upsert_channel(
                login=user.login,
                twitch_id=user.twitch_id,
                display_name=user.display_name,
                avatar_url=user.avatar_url,
                twitch_created_at=user.created_at,
                fetched_at=now,
            )

        await self._session.commit()

        total = len(page.items)
        counts = Counter(_to_schema_category(item.category) for item in page.items)
        denominator = total or 1

        return RoleList(
            channel=ChannelRead.model_validate(channel),
            items=[
                RoleRead(
                    twitch_id=item.user.twitch_id,
                    login=item.user.login,
                    display_name=item.user.display_name,
                    avatar_url=item.user.avatar_url,
                    category=_to_schema_category(item.category),
                    granted_at=item.granted_at,
                    twitch_created_at=item.user.created_at,
                )
                for item in page.items
            ],
            total=total,
            followers_total=page.followers_total,
            follows_total=page.follows_total,
            stats=[
                RoleStatRead(
                    category=category,
                    count=counts[category],
                    percent=round((counts[category] / denominator) * 100, 1),
                )
                for category in _ROLE_ORDER
            ],
        )

    async def aclose(self) -> None:
        if self._owns_role_client:
            await self._role_client.aclose()


def _to_schema_category(category: TwitchRoleCategory) -> RoleCategory:
    return RoleCategory(category.value)

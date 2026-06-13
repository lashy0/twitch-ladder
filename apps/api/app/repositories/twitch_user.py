import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import TwitchUser


class TwitchUserRepository:
    """Database access for local Twitch account projections."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository.

        Args:
            session: Active SQLAlchemy async session.
        """
        self._session = session

    async def get_by_id(self, user_id: uuid.UUID) -> TwitchUser | None:
        """Return a Twitch user by local database ID.

        Args:
            user_id: Local `twitch_users.id`.

        Returns:
            Matching user, or `None` when it does not exist.
        """
        return await self._session.get(TwitchUser, user_id)

    async def get_by_login(self, login: str) -> TwitchUser | None:
        """Return a Twitch user by normalized login.

        Args:
            login: Twitch login. The lookup is normalized to lowercase.

        Returns:
            Matching user, or `None` when it does not exist.
        """
        stmt = select(TwitchUser).where(TwitchUser.login == login.lower())
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_twitch_id(self, twitch_id: str) -> TwitchUser | None:
        """Return a Twitch user by Twitch user ID.

        Args:
            twitch_id: External Twitch user ID.

        Returns:
            Matching user, or `None` when it does not exist.
        """
        stmt = select(TwitchUser).where(TwitchUser.twitch_id == twitch_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert(
        self,
        *,
        login: str,
        twitch_id: str | None = None,
        display_name: str | None = None,
        avatar_url: str | None = None,
        twitch_created_at: datetime | None = None,
        fetched_at: datetime | None = None,
    ) -> TwitchUser:
        """Create or update a local Twitch account projection.

        Args:
            login: Twitch login. Stored lowercase.
            twitch_id: External Twitch user ID when known.
            display_name: Twitch display name for UI.
            avatar_url: Twitch avatar URL for UI.
            twitch_created_at: Twitch account creation time.
            fetched_at: Time when this projection was refreshed from Twitch.

        Returns:
            Created or updated user.
        """
        normalized_login = login.lower()
        user = await self.get_by_twitch_id(twitch_id) if twitch_id else None
        if user is None:
            user = await self.get_by_login(normalized_login)

        if user is None:
            user = TwitchUser(login=normalized_login)
            self._session.add(user)

        user.twitch_id = twitch_id
        user.login = normalized_login
        user.display_name = display_name
        user.avatar_url = avatar_url
        user.twitch_created_at = twitch_created_at
        user.fetched_at = fetched_at

        await self._session.flush()
        return user

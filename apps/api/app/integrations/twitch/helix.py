from typing import Literal

import httpx
from loguru import logger
from pydantic import BaseModel, Field

from app.core.config import settings
from app.integrations.twitch.auth import TwitchAppTokenProvider
from app.integrations.twitch.dto import TwitchUserData, TwitchVideoData, TwitchVideoPage
from app.integrations.twitch.exceptions import TwitchApiError
from app.integrations.twitch.utils import parse_rfc3339, parse_twitch_duration

HelixParamValue = str | int | float | bool | None


class _HelixUser(BaseModel):
    id: str
    login: str
    display_name: str
    profile_image_url: str | None = None
    created_at: str | None = None


class _HelixUsersResponse(BaseModel):
    data: list[_HelixUser]


class _HelixVideo(BaseModel):
    id: str
    user_id: str
    title: str
    published_at: str | None = None
    view_count: int | None = None
    thumbnail_url: str | None = None
    duration: str | None = None


class _HelixPagination(BaseModel):
    cursor: str | None = None


class _HelixVideosResponse(BaseModel):
    data: list[_HelixVideo]
    pagination: _HelixPagination = Field(default_factory=_HelixPagination)


class TwitchHelixClient:
    """Client for official Twitch Helix API endpoints."""

    def __init__(
        self,
        *,
        client: httpx.AsyncClient | None = None,
        token_provider: TwitchAppTokenProvider | None = None,
        client_id: str = settings.TWITCH_CLIENT_ID,
        base_url: str = settings.TWITCH_HELIX_BASE_URL,
    ) -> None:
        """Initialize the Helix client.

        Args:
            client: Optional shared HTTP client.
            token_provider: Optional Twitch app token provider.
            client_id: Twitch application client ID.
            base_url: Twitch Helix API base URL.
        """
        self._client = client or httpx.AsyncClient(timeout=settings.TWITCH_HTTP_TIMEOUT_SECONDS)
        self._owns_client = client is None
        self._token_provider = token_provider or TwitchAppTokenProvider(client=self._client)
        self._client_id = client_id
        self._base_url = base_url.rstrip("/")

    async def aclose(self) -> None:
        """Close owned HTTP resources."""
        if self._owns_client:
            await self._client.aclose()

    async def get_user_by_login(self, login: str) -> TwitchUserData | None:
        """Return one Twitch user by login.

        Args:
            login: Twitch login.

        Returns:
            User data, or `None` when Twitch returns no matching user.
        """
        users = await self.get_users_by_logins([login])
        return users[0] if users else None

    async def get_users_by_logins(self, logins: list[str]) -> list[TwitchUserData]:
        """Return Twitch users by login names.

        Args:
            logins: Twitch logins. Twitch allows up to 100 login query values.

        Returns:
            Normalized user records returned by Twitch.
        """
        if not logins:
            return []
        if len(logins) > 100:
            raise ValueError("Twitch Get Users supports at most 100 logins")

        logger.info("Fetching Twitch users by login count={count}", count=len(logins))
        response = await self._get(
            "/users",
            params=[("login", login.lower()) for login in logins],
        )
        payload = _HelixUsersResponse.model_validate(response)
        logger.info(
            "Fetched Twitch users requested={requested} returned={returned}",
            requested=len(logins),
            returned=len(payload.data),
        )
        return [
            TwitchUserData(
                twitch_id=user.id,
                login=user.login,
                display_name=user.display_name,
                avatar_url=user.profile_image_url,
                created_at=parse_rfc3339(user.created_at),
            )
            for user in payload.data
        ]

    async def list_videos_by_user_id(
        self,
        user_id: str,
        *,
        first: int = 40,
        after: str | None = None,
        video_type: Literal["all", "archive", "highlight", "upload"] = "archive",
    ) -> TwitchVideoPage:
        """Return one page of VODs for a Twitch user.

        Args:
            user_id: Twitch user ID.
            first: Page size from 1 to 100.
            after: Optional pagination cursor.
            video_type: Twitch video type filter.

        Returns:
            Normalized VOD page.
        """
        if first < 1 or first > 100:
            raise ValueError("Twitch Get Videos page size must be between 1 and 100")

        logger.info(
            "Fetching Twitch videos user_id={user_id} first={first} after={after} type={video_type}",
            user_id=user_id,
            first=first,
            after=after,
            video_type=video_type,
        )
        params: list[tuple[str, HelixParamValue]] = [
            ("user_id", user_id),
            ("first", first),
            ("type", video_type),
        ]
        if after is not None:
            params.append(("after", after))

        response = await self._get("/videos", params=params)
        payload = _HelixVideosResponse.model_validate(response)
        logger.info(
            "Fetched Twitch videos user_id={user_id} returned={returned} has_cursor={has_cursor}",
            user_id=user_id,
            returned=len(payload.data),
            has_cursor=payload.pagination.cursor is not None,
        )
        return TwitchVideoPage(
            items=[
                TwitchVideoData(
                    twitch_video_id=video.id,
                    channel_twitch_id=video.user_id,
                    title=video.title,
                    duration_seconds=parse_twitch_duration(video.duration),
                    published_at=parse_rfc3339(video.published_at),
                    view_count=video.view_count,
                    thumbnail_url=video.thumbnail_url,
                )
                for video in payload.data
            ],
            cursor=payload.pagination.cursor,
        )

    async def _get(
        self,
        path: str,
        *,
        params: list[tuple[str, HelixParamValue]],
    ) -> object:
        token = await self._token_provider.get_app_access_token()
        try:
            response = await self._client.get(
                f"{self._base_url}{path}",
                params=params,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Client-Id": self._client_id,
                },
            )
        except httpx.HTTPError as exc:
            logger.opt(exception=exc).warning(
                "Twitch Helix request failed path={path}",
                path=path,
            )
            raise TwitchApiError(f"Twitch Helix request failed: {path}") from exc

        if response.is_error:
            logger.warning(
                "Twitch Helix returned error path={path} status={status_code}",
                path=path,
                status_code=response.status_code,
            )
            raise TwitchApiError(
                f"Twitch Helix request failed with status {response.status_code}",
                status_code=response.status_code,
                response_body=response.text,
            )

        return response.json()

    async def __aenter__(self) -> "TwitchHelixClient":
        """Enter async context manager."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: object | None,
    ) -> None:
        """Exit async context manager and close owned resources."""
        await self.aclose()

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import httpx
from loguru import logger
from pydantic import BaseModel

from app.core.config import settings
from app.integrations.twitch.exceptions import TwitchAuthError


class _TokenResponse(BaseModel):
    access_token: str
    expires_in: int
    token_type: str


@dataclass(slots=True)
class _CachedToken:
    access_token: str
    expires_at: datetime


class TwitchAppTokenProvider:
    """Fetches and caches Twitch app access tokens."""

    def __init__(
        self,
        *,
        client: httpx.AsyncClient | None = None,
        client_id: str = settings.TWITCH_CLIENT_ID,
        client_secret: str = settings.TWITCH_CLIENT_SECRET.get_secret_value(),
        auth_base_url: str = settings.TWITCH_AUTH_BASE_URL,
    ) -> None:
        """Initialize the token provider.

        Args:
            client: Optional shared HTTP client.
            client_id: Twitch application client ID.
            client_secret: Twitch application client secret.
            auth_base_url: Twitch OAuth host.
        """
        self._client = client or httpx.AsyncClient(timeout=settings.TWITCH_HTTP_TIMEOUT_SECONDS)
        self._owns_client = client is None
        self._client_id = client_id
        self._client_secret = client_secret
        self._token_url = f"{auth_base_url.rstrip('/')}/oauth2/token"
        self._cached_token: _CachedToken | None = None

    async def aclose(self) -> None:
        """Close the owned HTTP client."""
        if self._owns_client:
            await self._client.aclose()

    async def get_app_access_token(self) -> str:
        """Return a valid Twitch app access token.

        Returns:
            Cached or newly fetched app access token.

        Raises:
            TwitchAuthError: If credentials are missing or Twitch rejects the request.
        """
        if self._cached_token is not None and self._cached_token.expires_at > (
            datetime.now(UTC) + timedelta(seconds=60)
        ):
            logger.debug("Using cached Twitch app access token")
            return self._cached_token.access_token

        if not self._client_id or not self._client_secret:
            logger.warning("Twitch app token requested without configured credentials")
            raise TwitchAuthError("Twitch client ID and secret are required")

        logger.info("Requesting Twitch app access token")
        try:
            response = await self._client.post(
                self._token_url,
                data={
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                    "grant_type": "client_credentials",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        except httpx.HTTPError as exc:
            logger.opt(exception=exc).warning("Failed to request Twitch app access token")
            raise TwitchAuthError("Failed to request Twitch app access token") from exc

        if response.is_error:
            logger.warning(
                "Twitch token request failed with status {status_code}",
                status_code=response.status_code,
            )
            raise TwitchAuthError(
                f"Twitch token request failed with status {response.status_code}"
            )

        token = _TokenResponse.model_validate(response.json())
        self._cached_token = _CachedToken(
            access_token=token.access_token,
            expires_at=datetime.now(UTC) + timedelta(seconds=token.expires_in),
        )
        logger.info("Twitch app access token acquired")
        return token.access_token

    async def __aenter__(self) -> "TwitchAppTokenProvider":
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

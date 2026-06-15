from datetime import timedelta
from secrets import token_urlsafe

from app.core.config import settings
from app.core.security import create_access_token, decode_access_token
from app.integrations.twitch.auth import TwitchAuthenticatedUser, TwitchUserOAuthClient
from app.schemas import AuthUserRead


class AuthService:
    """Application-level Twitch OAuth session flow."""

    def __init__(self, twitch_oauth: TwitchUserOAuthClient | None = None) -> None:
        self._twitch_oauth = twitch_oauth or TwitchUserOAuthClient()

    def create_oauth_state(self) -> str:
        return token_urlsafe(32)

    def build_twitch_login_url(self, state: str) -> str:
        return self._twitch_oauth.build_authorization_url(
            redirect_uri=settings.TWITCH_OAUTH_REDIRECT_URI,
            scopes=settings.TWITCH_OAUTH_SCOPES,
            state=state,
        )

    async def authenticate_twitch_code(self, code: str) -> AuthUserRead:
        user = await self._twitch_oauth.authenticate_code(
            code=code,
            redirect_uri=settings.TWITCH_OAUTH_REDIRECT_URI,
        )
        return self._to_schema(user)

    async def aclose(self) -> None:
        await self._twitch_oauth.aclose()

    def create_session_token(self, user: AuthUserRead) -> str:
        return create_access_token(
            {
                "sub": user.twitch_id,
                "login": user.login,
                "display_name": user.display_name,
                "avatar_url": user.avatar_url,
            },
            secret=self._session_secret,
            expires_delta=timedelta(seconds=settings.AUTH_COOKIE_MAX_AGE_SECONDS),
            issuer=settings.AUTH_JWT_ISSUER,
            audience=settings.AUTH_JWT_AUDIENCE,
        )

    def read_session_token(self, token: str | None) -> AuthUserRead | None:
        if token is None:
            return None

        payload = decode_access_token(
            token,
            secret=self._session_secret,
            issuer=settings.AUTH_JWT_ISSUER,
            audience=settings.AUTH_JWT_AUDIENCE,
        )
        if payload is None:
            return None

        twitch_id = payload.get("sub")
        login = payload.get("login")
        display_name = payload.get("display_name")
        avatar_url = payload.get("avatar_url")
        if (
            not isinstance(twitch_id, str)
            or not isinstance(login, str)
            or not isinstance(display_name, str)
        ):
            return None
        if avatar_url is not None and not isinstance(avatar_url, str):
            return None

        return AuthUserRead(
            twitch_id=twitch_id,
            login=login,
            display_name=display_name,
            avatar_url=avatar_url,
        )

    @property
    def _session_secret(self) -> str:
        explicit_secret = settings.AUTH_SESSION_SECRET.get_secret_value()
        if explicit_secret:
            return explicit_secret
        return settings.TWITCH_CLIENT_SECRET.get_secret_value()

    @staticmethod
    def _to_schema(user: TwitchAuthenticatedUser) -> AuthUserRead:
        return AuthUserRead(
            twitch_id=user.twitch_id,
            login=user.login,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
        )

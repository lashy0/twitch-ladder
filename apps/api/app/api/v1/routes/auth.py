from typing import Literal
from urllib.parse import urlencode

from fastapi import APIRouter, Cookie, Query, Response, status
from fastapi.responses import RedirectResponse

from app.core.config import settings
from app.core.exceptions import AppException
from app.integrations.twitch.exceptions import TwitchAuthError
from app.schemas import AuthSessionRead
from app.services import AuthService

router = APIRouter()

_OAUTH_STATE_COOKIE = "twitch_ladder_oauth_state"
_COOKIE_SAMESITE: Literal["lax"] = "lax"


@router.get("/twitch/login")
async def login_with_twitch() -> RedirectResponse:
    _ensure_auth_configured()
    service = AuthService()

    state = service.create_oauth_state()
    response = RedirectResponse(service.build_twitch_login_url(state))
    response.set_cookie(
        _OAUTH_STATE_COOKIE,
        state,
        max_age=600,
        httponly=True,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=_COOKIE_SAMESITE,
    )
    return response


@router.get("/twitch/callback")
async def twitch_callback(
    code: str = Query(""),
    state: str = Query(""),
    stored_state: str | None = Cookie(default=None, alias=_OAUTH_STATE_COOKIE),
) -> RedirectResponse:
    _ensure_auth_configured()

    if not code or not state or stored_state != state:
        response = _redirect_with_error("state")
        response.delete_cookie(_OAUTH_STATE_COOKIE, samesite=_COOKIE_SAMESITE)
        return response

    service = AuthService()
    try:
        user = await service.authenticate_twitch_code(code)
    except TwitchAuthError:
        response = _redirect_with_error("twitch")
        response.delete_cookie(_OAUTH_STATE_COOKIE, samesite=_COOKIE_SAMESITE)
        return response
    finally:
        await service.aclose()

    response = RedirectResponse(settings.WEB_APP_BASE_URL)
    response.delete_cookie(_OAUTH_STATE_COOKIE, samesite=_COOKIE_SAMESITE)
    response.set_cookie(
        settings.AUTH_COOKIE_NAME,
        service.create_session_token(user),
        max_age=settings.AUTH_COOKIE_MAX_AGE_SECONDS,
        httponly=True,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=_COOKIE_SAMESITE,
    )
    return response


@router.get("/me", response_model=AuthSessionRead)
async def get_current_user(
    session_token: str | None = Cookie(default=None, alias=settings.AUTH_COOKIE_NAME),
) -> AuthSessionRead:
    user = AuthService().read_session_token(session_token)
    return AuthSessionRead(authenticated=user is not None, user=user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response) -> None:
    response.delete_cookie(settings.AUTH_COOKIE_NAME, samesite=_COOKIE_SAMESITE)


def _redirect_with_error(reason: str) -> RedirectResponse:
    query = urlencode({"auth_error": reason})
    return RedirectResponse(f"{settings.WEB_APP_BASE_URL}?{query}")


def _ensure_auth_configured() -> None:
    if (
        not settings.TWITCH_CLIENT_ID
        or not settings.TWITCH_CLIENT_SECRET.get_secret_value()
    ):
        raise AppException(
            "Twitch OAuth is not configured",
            code="TWITCH_AUTH_NOT_CONFIGURED",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

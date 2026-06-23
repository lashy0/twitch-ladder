from fastapi import APIRouter, status

from app.api.deps import DbSession
from app.core.exceptions import AppException
from app.integrations.twitch.exceptions import TwitchApiError
from app.schemas import RoleList
from app.services import RoleService

router = APIRouter()


@router.get("/channels/{login}/roles", response_model=RoleList)
async def list_channel_roles(
    login: str,
    session: DbSession,
) -> RoleList:
    service = RoleService(session)
    try:
        return await service.get(login)
    except TwitchApiError as exc:
        if exc.status_code == 404:
            raise AppException(
                "Channel not found",
                code="CHANNEL_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND,
            ) from exc
        raise AppException(
            "Twitch role data is unavailable",
            code="TWITCH_ROLES_UNAVAILABLE",
            status_code=status.HTTP_502_BAD_GATEWAY,
            details={"twitch_error": exc.response_body} if exc.response_body else None,
        ) from exc
    finally:
        await service.aclose()

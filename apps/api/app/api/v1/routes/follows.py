from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.deps import DbSession
from app.core.exceptions import AppException
from app.integrations.twitch.exceptions import TwitchApiError
from app.schemas import FollowList
from app.services import FollowService

router = APIRouter()

LimitQuery = Annotated[int, Query(ge=1, le=100)]


@router.get("/channels/{login}/follows", response_model=FollowList)
async def list_channel_follows(
    login: str,
    session: DbSession,
    limit: LimitQuery = 100,
    after: str | None = None,
) -> FollowList:
    service = FollowService(session)
    try:
        result = await service.get(login, limit=limit, after=after)
    except TwitchApiError as exc:
        raise AppException(
            "Twitch follow data is unavailable",
            code="TWITCH_FOLLOWS_UNAVAILABLE",
            status_code=status.HTTP_502_BAD_GATEWAY,
        ) from exc
    finally:
        await service.aclose()

    if result is None:
        raise AppException(
            "Channel not found",
            code="CHANNEL_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return result

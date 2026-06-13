from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.deps import DbSession
from app.core.exceptions import AppException
from app.schemas import LadderEntry, LadderRead
from app.services import ChannelService, LadderService

router = APIRouter()

LimitQuery = Annotated[int, Query(ge=1, le=500)]
OffsetQuery = Annotated[int, Query(ge=0)]


@router.get("/channels/{login}/ladder", response_model=LadderRead)
async def get_channel_ladder(
    login: str,
    session: DbSession,
    limit: LimitQuery = 100,
    offset: OffsetQuery = 0,
) -> LadderRead:
    channel = await ChannelService(session).get_by_login(login)
    if channel is None:
        raise AppException(
            "Channel not found",
            code="CHANNEL_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    ladder = await LadderService(session).get_by_channel(
        channel.id,
        limit=limit,
        offset=offset,
    )

    return LadderRead(
        channel_id=ladder.channel_id,
        videos_count=ladder.videos_count,
        total_messages=ladder.total_messages,
        unique_chatters=ladder.unique_chatters,
        items=[
            LadderEntry(
                rank=offset + index + 1,
                user_id=row.user_id,
                user_login=row.user_login,
                user_display_name=row.user_display_name,
                message_count=row.message_count,
                videos_count=row.videos_count,
                first_message_at=row.first_message_at,
                last_message_at=row.last_message_at,
            )
            for index, row in enumerate(ladder.rows)
        ],
    )

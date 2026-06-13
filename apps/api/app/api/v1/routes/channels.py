from fastapi import APIRouter, status

from app.api.deps import DbSession
from app.core.exceptions import AppException
from app.schemas import ChannelRead, ChannelSummary
from app.services import ChannelService

router = APIRouter()


@router.get("/{login}", response_model=ChannelRead)
async def get_channel(login: str, session: DbSession) -> ChannelRead:
    service = ChannelService(session)
    channel = await service.get_by_login(login)
    if channel is None:
        raise AppException(
            "Channel not found",
            code="CHANNEL_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return ChannelRead.model_validate(channel)


@router.get("/{login}/summary", response_model=ChannelSummary)
async def get_channel_summary(login: str, session: DbSession) -> ChannelSummary:
    service = ChannelService(session)
    channel = await service.get_by_login(login)
    if channel is None:
        raise AppException(
            "Channel not found",
            code="CHANNEL_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    videos_count, scanned_videos_count, total_messages, unique_chatters = (
        await service.get_summary_counts(channel.id)
    )

    return ChannelSummary(
        channel=ChannelRead.model_validate(channel),
        videos_count=videos_count,
        scanned_videos_count=scanned_videos_count,
        total_messages=total_messages,
        unique_chatters=unique_chatters,
    )

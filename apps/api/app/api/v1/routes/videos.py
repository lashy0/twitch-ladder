import uuid
from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.deps import DbSession
from app.core.exceptions import AppException
from app.schemas import ScanJobRead, VideoList, VideoRead
from app.services import ChannelService, ScanJobService, VideoService

router = APIRouter()

LimitQuery = Annotated[int, Query(ge=1, le=100)]
OffsetQuery = Annotated[int, Query(ge=0)]


@router.get("/channels/{login}/videos", response_model=VideoList)
async def list_channel_videos(
    login: str,
    session: DbSession,
    limit: LimitQuery = 40,
    offset: OffsetQuery = 0,
) -> VideoList:
    channel_service = ChannelService(session)
    channel = await channel_service.get_by_login(login)
    if channel is None:
        raise AppException(
            "Channel not found",
            code="CHANNEL_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    video_service = VideoService(session)
    videos = await video_service.list_by_channel(
        channel.id,
        limit=limit,
        offset=offset,
    )
    total = await video_service.count_by_channel(channel.id)

    return VideoList(
        items=[VideoRead.model_validate(video) for video in videos],
        total=total,
    )


@router.post(
    "/videos/{video_id}/scan",
    response_model=ScanJobRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_video_scan_job(video_id: uuid.UUID, session: DbSession) -> ScanJobRead:
    video_service = VideoService(session)
    video = await video_service.get_by_id(video_id)
    if video is None:
        raise AppException(
            "Video not found",
            code="VIDEO_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    job = await ScanJobService(session).create_vod_chat_job(video_id)
    await session.commit()

    return ScanJobRead.model_validate(job)

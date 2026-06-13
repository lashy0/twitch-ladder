import uuid
from datetime import datetime

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ScanJob
from app.repositories import ScanJobRepository, VideoRepository
from app.shared.enums import ScanJobStatus, VideoChatScanStatus


class ScanJobService:
    """Use cases for VOD scan job lifecycle changes."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the service.

        Args:
            session: Active SQLAlchemy async session.
        """
        self._jobs = ScanJobRepository(session)
        self._videos = VideoRepository(session)

    async def get_by_id(self, job_id: uuid.UUID) -> ScanJob | None:
        """Return a scan job by local database ID.

        Args:
            job_id: Local `scan_jobs.id`.

        Returns:
            Matching job, or `None` when it does not exist.
        """
        return await self._jobs.get_by_id(job_id)

    async def create_vod_chat_job(self, video_id: uuid.UUID) -> ScanJob:
        """Create a pending VOD chat scan job.

        Args:
            video_id: Local VOD ID to scan.

        Returns:
            Created scan job.
        """
        job = await self._jobs.create(video_id=video_id, kind="vod_chat")
        await self._videos.update_chat_scan_status(video_id, VideoChatScanStatus.PENDING)
        logger.info(
            "Created VOD chat scan job job_id={job_id} video_id={video_id}",
            job_id=job.id,
            video_id=video_id,
        )
        return job

    async def mark_running(
        self,
        job_id: uuid.UUID,
        *,
        started_at: datetime,
    ) -> ScanJob | None:
        """Mark a scan job and its VOD as running.

        Args:
            job_id: Local `scan_jobs.id`.
            started_at: Time when execution started.

        Returns:
            Updated job, or `None` when it does not exist.
        """
        job = await self._jobs.update_progress(
            job_id,
            status=ScanJobStatus.RUNNING,
            started_at=started_at,
        )
        if job is not None:
            await self._videos.update_chat_scan_status(
                job.video_id,
                VideoChatScanStatus.RUNNING,
            )
            logger.info(
                "Marked scan job running job_id={job_id} video_id={video_id}",
                job_id=job.id,
                video_id=job.video_id,
            )
        return job

    async def mark_completed(
        self,
        job_id: uuid.UUID,
        *,
        processed_messages: int,
        finished_at: datetime,
    ) -> ScanJob | None:
        """Mark a scan job and its VOD as completed.

        Args:
            job_id: Local `scan_jobs.id`.
            processed_messages: Final number of processed messages.
            finished_at: Time when execution finished.

        Returns:
            Updated job, or `None` when it does not exist.
        """
        job = await self._jobs.update_progress(
            job_id,
            status=ScanJobStatus.COMPLETED,
            progress_percent=100,
            processed_messages=processed_messages,
            finished_at=finished_at,
        )
        if job is not None:
            await self._videos.update_chat_scan_status(
                job.video_id,
                VideoChatScanStatus.COMPLETED,
            )
            logger.info(
                "Marked scan job completed job_id={job_id} video_id={video_id} processed_messages={processed_messages}",
                job_id=job.id,
                video_id=job.video_id,
                processed_messages=processed_messages,
            )
        return job

    async def mark_failed(
        self,
        job_id: uuid.UUID,
        *,
        error_message: str,
        finished_at: datetime,
    ) -> ScanJob | None:
        """Mark a scan job and its VOD as failed.

        Args:
            job_id: Local `scan_jobs.id`.
            error_message: Failure reason.
            finished_at: Time when execution failed.

        Returns:
            Updated job, or `None` when it does not exist.
        """
        job = await self._jobs.update_progress(
            job_id,
            status=ScanJobStatus.FAILED,
            error_message=error_message,
            finished_at=finished_at,
        )
        if job is not None:
            await self._videos.update_chat_scan_status(
                job.video_id,
                VideoChatScanStatus.FAILED,
            )
            logger.warning(
                "Marked scan job failed job_id={job_id} video_id={video_id} error_message={error_message}",
                job_id=job.id,
                video_id=job.video_id,
                error_message=error_message,
            )
        return job

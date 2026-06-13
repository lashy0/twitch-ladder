import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ScanJob
from app.shared.enums import ScanJobStatus


class ScanJobRepository:
    """Database access for persistent VOD scan jobs."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository.

        Args:
            session: Active SQLAlchemy async session.
        """
        self._session = session

    async def get_by_id(self, job_id: uuid.UUID) -> ScanJob | None:
        """Return a scan job by local database ID.

        Args:
            job_id: Local `scan_jobs.id`.

        Returns:
            Matching scan job, or `None` when it does not exist.
        """
        return await self._session.get(ScanJob, job_id)

    async def create(
        self,
        *,
        video_id: uuid.UUID,
        kind: str = "vod_chat",
    ) -> ScanJob:
        """Create a pending scan job.

        Args:
            video_id: Local VOD ID to scan.
            kind: Type of scan job.

        Returns:
            Created scan job.
        """
        job = ScanJob(video_id=video_id, kind=kind)
        self._session.add(job)
        await self._session.flush()
        return job

    async def update_progress(
        self,
        job_id: uuid.UUID,
        *,
        status: ScanJobStatus | None = None,
        progress_percent: int | None = None,
        processed_messages: int | None = None,
        total_messages_estimate: int | None = None,
        error_message: str | None = None,
        started_at: datetime | None = None,
        finished_at: datetime | None = None,
    ) -> ScanJob | None:
        """Update mutable scan job progress fields.

        Args:
            job_id: Local `scan_jobs.id`.
            status: Optional new job status.
            progress_percent: Optional progress from 0 to 100.
            processed_messages: Optional number of processed chat messages.
            total_messages_estimate: Optional estimate of total messages.
            error_message: Optional failure message.
            started_at: Optional execution start time.
            finished_at: Optional execution finish time.

        Returns:
            Updated scan job, or `None` when it does not exist.
        """
        job = await self.get_by_id(job_id)
        if job is None:
            return None

        if status is not None:
            job.status = status
        if progress_percent is not None:
            job.progress_percent = progress_percent
        if processed_messages is not None:
            job.processed_messages = processed_messages
        if total_messages_estimate is not None:
            job.total_messages_estimate = total_messages_estimate
        if error_message is not None:
            job.error_message = error_message
        if started_at is not None:
            job.started_at = started_at
        if finished_at is not None:
            job.finished_at = finished_at

        await self._session.flush()
        return job

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.shared.enums import ScanJobStatus

if TYPE_CHECKING:
    from app.models.video import Video


class ScanJob(Base):
    """Persistent state for long-running VOD scans.

    HTTP requests should create or read jobs; workers/background tasks should
    update progress and final status.
    """

    __tablename__ = "scan_jobs"
    __table_args__ = (
        CheckConstraint(
            "progress_percent >= 0 AND progress_percent <= 100",
            name="ck_scan_jobs_progress_percent",
        ),
        CheckConstraint("processed_messages >= 0"),
        CheckConstraint("total_messages_estimate IS NULL OR total_messages_estimate >= 0"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    video_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("videos.id", ondelete="CASCADE"),
        index=True,
    )
    kind: Mapped[str] = mapped_column(String(64), default="vod_chat")
    status: Mapped[ScanJobStatus] = mapped_column(
        Enum(
            ScanJobStatus,
            name="scan_job_status",
            native_enum=False,
            values_callable=lambda statuses: [status.value for status in statuses],
            create_constraint=True,
            validate_strings=True,
        ),
        default=ScanJobStatus.PENDING,
        index=True,
    )
    progress_percent: Mapped[int] = mapped_column(Integer, default=0)
    processed_messages: Mapped[int] = mapped_column(Integer, default=0)
    total_messages_estimate: Mapped[int | None] = mapped_column(Integer)
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    video: Mapped["Video"] = relationship(back_populates="scan_jobs")

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
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.shared.enums import VideoChatScanStatus

if TYPE_CHECKING:
    from app.models.scan_job import ScanJob
    from app.models.twitch_user import TwitchUser
    from app.models.video_chatter import VideoChatter


class Video(Base):
    """Twitch VOD known to the application.

    The row gives scan jobs and ladder aggregates a stable local target instead
    of passing raw Twitch video IDs through every backend layer.
    """

    __tablename__ = "videos"
    __table_args__ = (
        CheckConstraint("duration_seconds IS NULL OR duration_seconds >= 0"),
        CheckConstraint("view_count IS NULL OR view_count >= 0"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    twitch_video_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    channel_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("twitch_users.id", ondelete="CASCADE"),
        index=True,
    )
    title: Mapped[str] = mapped_column(String(512))
    duration_seconds: Mapped[int | None] = mapped_column(Integer)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    view_count: Mapped[int | None] = mapped_column(Integer)
    thumbnail_url: Mapped[str | None] = mapped_column(String(2048))
    chat_scan_status: Mapped[VideoChatScanStatus] = mapped_column(
        Enum(
            VideoChatScanStatus,
            name="video_chat_scan_status",
            native_enum=False,
            values_callable=lambda statuses: [status.value for status in statuses],
            create_constraint=True,
            validate_strings=True,
        ),
        default=VideoChatScanStatus.NOT_SCANNED,
    )
    fetched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    channel: Mapped["TwitchUser"] = relationship(back_populates="videos")
    scan_jobs: Mapped[list["ScanJob"]] = relationship(back_populates="video")
    chatters: Mapped[list["VideoChatter"]] = relationship(back_populates="video")

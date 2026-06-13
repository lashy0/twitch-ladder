import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.twitch_user import TwitchUser
    from app.models.video import Video


class VideoChatter(Base):
    """Per-user chat activity aggregate for one VOD.

    `user_login` is stored as a required snapshot from chat data. `user_id` is
    optional so VOD scans do not need to resolve every chatter profile first.
    """

    __tablename__ = "video_chatters"
    __table_args__ = (
        UniqueConstraint("video_id", "user_login", name="uq_video_chatters_video_login"),
        CheckConstraint("message_count >= 0"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    video_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("videos.id", ondelete="CASCADE"),
        index=True,
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("twitch_users.id", ondelete="SET NULL"),
        index=True,
    )
    user_login: Mapped[str] = mapped_column(String(128), index=True)
    user_display_name: Mapped[str | None] = mapped_column(String(128))
    message_count: Mapped[int] = mapped_column(Integer, default=0)
    first_message_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_message_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    video: Mapped["Video"] = relationship(back_populates="chatters")
    user: Mapped["TwitchUser | None"] = relationship(back_populates="chat_entries")

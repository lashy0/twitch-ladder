import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.video import Video
    from app.models.video_chatter import VideoChatter


class TwitchUser(Base):
    """Local projection of a Twitch account.

    Used for channels immediately and can later be linked to chatters during
    profile enrichment. Keep Twitch API response shapes out of this model.
    """

    __tablename__ = "twitch_users"
    __table_args__ = (
        CheckConstraint("login = lower(login)", name="ck_twitch_users_login_lowercase"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    twitch_id: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)
    login: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    display_name: Mapped[str | None] = mapped_column(String(128))
    avatar_url: Mapped[str | None] = mapped_column(String(2048))
    twitch_created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
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

    videos: Mapped[list["Video"]] = relationship(back_populates="channel")
    chat_entries: Mapped[list["VideoChatter"]] = relationship(back_populates="user")

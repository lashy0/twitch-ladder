import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class LadderRow:
    """Read model row for channel ladder results."""

    user_id: uuid.UUID | None
    user_login: str
    user_display_name: str | None
    message_count: int
    videos_count: int
    first_message_at: datetime | None
    last_message_at: datetime | None


@dataclass(frozen=True, slots=True)
class LadderResult:
    """Aggregated ladder result for one channel."""

    channel_id: uuid.UUID
    videos_count: int
    total_messages: int
    unique_chatters: int
    rows: list[LadderRow]

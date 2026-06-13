import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class VideoChatterAggregate:
    """Input data for one chatter aggregate in one VOD."""

    user_login: str
    user_id: uuid.UUID | None = None
    user_display_name: str | None = None
    message_count: int = 0
    first_message_at: datetime | None = None
    last_message_at: datetime | None = None

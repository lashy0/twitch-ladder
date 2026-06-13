import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.shared.enums import ScanJobStatus


class ScanJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    video_id: uuid.UUID
    kind: str
    status: ScanJobStatus
    progress_percent: int
    processed_messages: int
    total_messages_estimate: int | None
    error_message: str | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime
    updated_at: datetime

import uuid

from fastapi import APIRouter, status

from app.api.deps import DbSession
from app.core.exceptions import AppException
from app.schemas import ScanJobRead
from app.services import ScanJobService

router = APIRouter()


@router.get("/{job_id}", response_model=ScanJobRead)
async def get_scan_job(job_id: uuid.UUID, session: DbSession) -> ScanJobRead:
    job = await ScanJobService(session).get_by_id(job_id)
    if job is None:
        raise AppException(
            "Scan job not found",
            code="SCAN_JOB_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return ScanJobRead.model_validate(job)

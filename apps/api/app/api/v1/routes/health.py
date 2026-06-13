from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("")
async def health() -> dict[str, str]:
    return {"status": "ok", "services": settings.PROJECT_NAME}

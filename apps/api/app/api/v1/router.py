from fastapi import APIRouter

from app.api.v1.routes import (
    auth,
    channels,
    follows,
    health,
    ladder,
    roles,
    scan_jobs,
    videos,
)

router = APIRouter()

router.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"],
)

router.include_router(
    channels.router,
    prefix="/channels",
    tags=["channels"],
)

router.include_router(
    health.router,
    prefix="/health",
    tags=["health"],
)

router.include_router(
    follows.router,
    tags=["follows"],
)

router.include_router(
    ladder.router,
    tags=["ladder"],
)

router.include_router(
    roles.router,
    tags=["roles"],
)

router.include_router(
    scan_jobs.router,
    prefix="/scan-jobs",
    tags=["scan-jobs"],
)

router.include_router(
    videos.router,
    tags=["videos"],
)

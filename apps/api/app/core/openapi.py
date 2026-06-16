from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.core.config import settings


def build_openapi_schema(app: FastAPI) -> dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=settings.PROJECT_NAME,
        version="0.1.0",
        routes=app.routes,
    )
    prefix = settings.API_V1_PREFIX.rstrip("/")
    paths = schema.get("paths")

    if isinstance(paths, dict) and prefix:
        schema["paths"] = {
            path.removeprefix(prefix) if path.startswith(f"{prefix}/") else path: value
            for path, value in paths.items()
        }

    schema["servers"] = [{"url": prefix or "/"}]
    app.openapi_schema = schema
    return schema

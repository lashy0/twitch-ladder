from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import router as api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handler
from app.core.logging import setup_logging
from app.core.openapi import build_openapi_schema

setup_logging()

app = FastAPI(
    debug=settings.DEBUG,
    title=settings.PROJECT_NAME,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

register_exception_handler(app)

app.include_router(api_router)


def custom_openapi() -> dict[str, object]:
    return build_openapi_schema(app)


app.openapi = custom_openapi  # type: ignore[method-assign]
app.router.routes = [
    route for route in app.router.routes if getattr(route, "path", None) != app.openapi_url
]


@app.get(app.openapi_url or "/openapi.json", include_in_schema=False)
async def openapi_schema() -> JSONResponse:
    return JSONResponse(app.openapi())

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

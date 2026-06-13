from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger


class AppException(Exception):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    code: str = "INTERNAL_SERVER_ERROR"
    message: str = "Internal Server Error"

    def __init__(
        self,
        message: str | None = None,
        *,
        code: str | None = None,
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message or self.message
        self.code = code or self.code
        self.status_code = status_code or self.status_code
        self.details = details
        super().__init__(self.message)


def build_error_response(
    *,
    code: str,
    message: str,
    status_code: int,
    path: str,
    details: dict[str, Any] | list[Any] | None = None,
) -> dict[str, Any]:
    return {
        "error": {
            "code": code,
            "message": message,
            "status_code": status_code,
            "path": path,
            "details": details,
        }
    }


def register_exception_handler(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request, exc: AppException
    ) -> JSONResponse:
        logger.warning(f"Application error: {exc.code} - {exc.message}")

        return JSONResponse(
            status_code=exc.status_code,
            content=build_error_response(
                code=exc.code,
                message=exc.message,
                status_code=exc.status_code,
                path=request.url.path,
                details=exc.details,
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        logger.warning(
            f"Request validation error on {request.url.path}: {exc.errors()}"
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=build_error_response(
                code="VALIDATION_ERROR",
                message="Request validation error",
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                path=request.url.path,
                details=list(exc.errors()),
            ),
        )

    @app.exception_handler(Exception)
    async def unexpected_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.opt(exception=exc).error(f"Unhandled error on {request.url.path}")

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=build_error_response(
                code="INTERNAL_SERVER_ERROR",
                message="Internal server error",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                path=request.url.path,
            ),
        )

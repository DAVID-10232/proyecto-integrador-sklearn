"""
Excepciones personalizadas y handlers globales.
Cumple el requisito: "Validación de datos y manejo de errores".
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Excepción base de la aplicación."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code


class ModelNotReadyError(AppError):
    def __init__(self):
        super().__init__("Model is not ready", status_code=503)


class InvalidInputError(AppError):
    def __init__(self, detail: str = "Invalid input"):
        super().__init__(detail, status_code=422)


class UnauthorizedError(AppError):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(detail, status_code=401)


# ---------- HANDLERS GLOBALES ----------

async def app_error_handler(request: Request, exc: AppError):
    logger.warning(f"AppError: {exc.message} — path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "path": request.url.path,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


async def validation_error_handler(
    request: Request, exc: RequestValidationError
):
    logger.warning(f"Validation error — path: {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": True,
            "message": "Validation failed",
            "details": exc.errors(),
            "path": request.url.path,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


async def generic_error_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "path": request.url.path,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )

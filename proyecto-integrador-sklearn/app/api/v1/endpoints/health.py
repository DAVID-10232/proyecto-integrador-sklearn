from fastapi import APIRouter
from app.core.config import settings
from app.ml.model import sentiment_model
from app.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy" if sentiment_model.is_loaded else "degraded",
        version=settings.VERSION,
        model_loaded=sentiment_model.is_loaded,
        model_name=sentiment_model.model_name,
    )


@router.get("/info")
async def info():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "model": sentiment_model.info(),
    }

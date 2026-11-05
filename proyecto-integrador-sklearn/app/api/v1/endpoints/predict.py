from fastapi import APIRouter, Depends, HTTPException
import time

from app.api.deps import get_current_user
from app.core.config import settings
from app.ml.model import sentiment_model
from app.schemas import (
    PredictRequest,
    PredictResponse,
    BatchPredictRequest,
    BatchPredictResponse,
)
from app.metrics.prometheus import (
    PREDICTIONS_TOTAL,
    PREDICTION_LATENCY,
    PREDICTION_ERRORS,
)

router = APIRouter()


@router.post("/", response_model=PredictResponse)
async def predict(
    payload: PredictRequest,
    user: str = Depends(get_current_user),
):
    if not sentiment_model.is_loaded:
        PREDICTION_ERRORS.inc()
        raise HTTPException(status_code=503, detail="Model not ready")

    start = time.perf_counter()
    try:
        result = sentiment_model.predict(payload.text)
    except Exception as e:
        PREDICTION_ERRORS.inc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        PREDICTION_LATENCY.observe(time.perf_counter() - start)

    PREDICTIONS_TOTAL.labels(label=result["label"]).inc()

    # ⚠️ IMPORTANTE: los 3 campos deben estar
    return PredictResponse(
        label=result["label"],
        score=result["score"],       # ← verificar que existe
        model=settings.MODEL_NAME,
    )


@router.post("/batch", response_model=BatchPredictResponse)
async def predict_batch(
    payload: BatchPredictRequest,
    user: str = Depends(get_current_user),
):
    if not sentiment_model.is_loaded:
        PREDICTION_ERRORS.inc()
        raise HTTPException(status_code=503, detail="Model not ready")

    start = time.perf_counter()
    try:
        results = sentiment_model.predict_batch(payload.texts)
    except Exception as e:
        PREDICTION_ERRORS.inc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        PREDICTION_LATENCY.observe(time.perf_counter() - start)

    for r in results:
        PREDICTIONS_TOTAL.labels(label=r["label"]).inc()

    return BatchPredictResponse(
        results=[
            PredictResponse(
                label=r["label"],
                score=r["score"],
                model=settings.MODEL_NAME,
            )
            for r in results
        ]
    )

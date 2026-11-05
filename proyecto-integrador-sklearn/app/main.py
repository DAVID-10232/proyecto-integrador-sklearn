from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from prometheus_fastapi_instrumentator import Instrumentator
import logging
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse

from app.core.config import settings
from app.core.exceptions import (
    AppError,
    app_error_handler,
    validation_error_handler,
    generic_error_handler,
)
from app.api.v1.router import api_router
from app.ml.model import sentiment_model
from app.automation.scheduler import start_scheduler, stop_scheduler
from app.metrics.prometheus import MODEL_LOADED, APP_INFO

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting AI Service...")

    ok = sentiment_model.load(settings.MODEL_PATH, settings.MODEL_NAME)
    MODEL_LOADED.set(1 if ok else 0)
    APP_INFO.labels(version=settings.VERSION).set(1)

    if settings.ENABLE_SCHEDULER:
        start_scheduler()

    logger.info("✅ AI Service ready")
    yield
    logger.info("🛑 Shutting down...")
    stop_scheduler()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "API segura que expone un modelo preentrenado de scikit-learn "
        "con métricas Prometheus y automatización."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# HANDLERS GLOBALES DE ERROR
# ============================================================
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(Exception, generic_error_handler)

# Routers
app.include_router(api_router, prefix=settings.API_V1_STR)

# Prometheus
Instrumentator().instrument(app).expose(
    app, endpoint="/metrics", include_in_schema=False
)


@app.get("/")
async def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics",
    }


@app.get("/health")
async def root_health():
    return {
        "status": "healthy" if sentiment_model.is_loaded else "degraded",
        "model_loaded": sentiment_model.is_loaded,
    }

STATIC_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "static"
)
os.makedirs(STATIC_DIR, exist_ok=True)

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)


STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/dashboard", include_in_schema=False)
async def dashboard():
    path = os.path.join(STATIC_DIR, "dashboard.html")
    if os.path.exists(path):
        return FileResponse(path)
    return HTMLResponse("<h1>Dashboard no encontrado</h1>", status_code=404)
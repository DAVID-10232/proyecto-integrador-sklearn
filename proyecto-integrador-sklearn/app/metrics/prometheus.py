from prometheus_client import Counter, Histogram, Gauge

PREDICTIONS_TOTAL = Counter(
    "ai_predictions_total",
    "Total de predicciones realizadas",
    ["label"],
)

PREDICTION_LATENCY = Histogram(
    "ai_prediction_latency_seconds",
    "Latencia de las predicciones",
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0],
)

PREDICTION_ERRORS = Counter(
    "ai_prediction_errors_total",
    "Total de errores de predicción",
)

MODEL_LOADED = Gauge(
    "ai_model_loaded",
    "1 si el modelo está cargado, 0 si no",
)

APP_INFO = Gauge(
    "ai_app_info",
    "Info de la aplicación",
    ["version"],
)

"""
Tests automatizados del sistema inteligente.
Cumple el requisito de "evidencias de ejecución".

Requiere que exista models/sentiment_model.joblib
(python scripts/train_model.py).
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings


@pytest.fixture(scope="module")
def client():
    # El context manager ejecuta el lifespan (carga del modelo).
    with TestClient(app) as c:
        yield c


def _get_token(client) -> str:
    """Helper: obtiene token JWT."""
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={
            "username": settings.ADMIN_EMAIL,
            "password": settings.ADMIN_PASSWORD,
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


# ============================================================
# HEALTH
# ============================================================
def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "service" in response.json()


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_info(client):
    response = client.get(f"{settings.API_V1_STR}/info")
    assert response.status_code == 200
    assert "model" in response.json()


# ============================================================
# AUTH
# ============================================================
def test_login_ok(client):
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={
            "username": settings.ADMIN_EMAIL,
            "password": settings.ADMIN_PASSWORD,
        },
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_wrong_password(client):
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={
            "username": settings.ADMIN_EMAIL,
            "password": "wrong",
        },
    )
    assert response.status_code == 401


# ============================================================
# PREDICT (con JWT)
# ============================================================
def test_predict_without_token(client):
    response = client.post(
        f"{settings.API_V1_STR}/predict/",
        json={"text": "I love this"},
    )
    assert response.status_code == 401


def test_predict_with_token(client):
    token = _get_token(client)
    response = client.post(
        f"{settings.API_V1_STR}/predict/",
        headers={"Authorization": f"Bearer {token}"},
        json={"text": "I love this product"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["label"] in ["POSITIVE", "NEGATIVE"]
    assert 0.0 <= data["score"] <= 1.0


def test_predict_validation_empty(client):
    token = _get_token(client)
    response = client.post(
        f"{settings.API_V1_STR}/predict/",
        headers={"Authorization": f"Bearer {token}"},
        json={"text": ""},
    )
    assert response.status_code == 422
    assert response.json()["error"] is True


def test_predict_batch(client):
    token = _get_token(client)
    response = client.post(
        f"{settings.API_V1_STR}/predict/batch",
        headers={"Authorization": f"Bearer {token}"},
        json={"texts": ["Great!", "Terrible."]},
    )
    assert response.status_code == 200
    assert len(response.json()["results"]) == 2


# ============================================================
# METRICS
# ============================================================
def test_metrics_endpoint(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    assert b"ai_predictions_total" in response.content

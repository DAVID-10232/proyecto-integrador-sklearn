# 🧠 RikiNode AI Service — Proyecto Integrador

Sistema inteligente de análisis de sentimiento basado en un modelo preentrenado (TF-IDF + LogisticRegression), expuesto mediante una API REST segura (JWT), contenerizada con Docker, automatizada con GitHub Actions y monitoreada con Prometheus.

> **Curso:** Implementación de Sistemas Inteligentes  
> **Semana:** 17 (Entrega Final)  
> **Estado:** ✅ Completado — 100/100 en pruebas automatizadas.

---

## ✨ Características Principales

- **Modelo Preentrenado:** Pipeline de `scikit-learn` (TF-IDF + LogisticRegression) serializado con `joblib`.
- **API Segura:** FastAPI + OAuth2 con JSON Web Tokens (JWT) y contraseñas hasheadas con `bcrypt`.
- **Validación Robusta:** Pydantic para validación de datos (texto vacío, longitud máxima) y manejo global de errores (401, 422, 500).
- **Contenerización:** Docker con compilación multietapa (*multi-stage build*) e imagen final ligera (~300 MB).
- **Orquestación:** `docker-compose.yml` con políticas de reinicio y *healthchecks*.
- **Automatización:** Tarea programada (APScheduler) para verificar el estado del modelo cada 5 minutos + Pipeline CI/CD.
- **Observabilidad:** Métricas expuestas en formato Prometheus (`/metrics`).
- **Dashboard Interactivo:** Interfaz gráfica web con gráficos en tiempo real (Chart.js) y suite de pruebas integrada.

---

## 📂 Estructura del Proyecto

El proyecto está organizado de forma modular para facilitar su mantenimiento y escalabilidad:

```text
proyecto-integrador-sklearn/
│
├── app/                            # Código fuente de la API
│   ├── main.py                     # Punto de entrada (FastAPI + Lifespan)
│   ├── schemas.py                  # Modelos de validación (Pydantic)
│   │
│   ├── core/                       # Configuración y Seguridad
│   │   ├── config.py               # Variables de entorno (.env)
│   │   ├── security.py             # Hashing bcrypt y generación de JWT
│   │   └── exceptions.py           # Handlers globales de errores
│   │
│   ├── api/                        # Enrutamiento y Endpoints
│   │   ├── deps.py                 # Dependencias (validación del token)
│   │   └── v1/
│   │       ├── router.py           # Enrutador principal v1
│   │       └── endpoints/
│   │           ├── auth.py         # Login y generación de token
│   │           ├── predict.py      # Inferencia individual y por lote
│   │           └── health.py       # Health checks e info del servicio
│   │
│   ├── ml/                         # Lógica de Machine Learning
│   │   └── model.py                # Carga del .joblib y método predict
│   │
│   ├── metrics/                    # Observabilidad
│   │   └── prometheus.py           # Definición de Counters y Histograms
│   │
│   └── automation/                 # Tareas en segundo plano
│       └── scheduler.py            # APScheduler (health check periódico)
│
├── static/                         # Interfaz de Usuario
│   └── dashboard.html              # Dashboard interactivo (Chart.js)
│
├── scripts/                        # Scripts utilitarios
│   ├── train_model.py              # Entrena y exporta el modelo .joblib
│   ├── load_test.py                # Prueba de carga (HTTPX)
│   └── test_completo.py            # Suite de 20 pruebas de integración
│
├── tests/                          # Pruebas unitarias
│   └── test_api.py                 # 10 tests con Pytest
│
├── models/                         # Artefactos del modelo
│   └── sentiment_model.joblib      # Modelo serializado (incluido)
│
├── .github/workflows/deploy.yml    # CI/CD (GitHub Actions)
├── .vscode/                        # Configuración de VS Code (launch.json)
├── Dockerfile                      # Imagen de producción (Multi-stage)
├── docker-compose.yml              # Orquestación local
├── requirements.txt                # Dependencias de producción
├── requirements-dev.txt            # Dependencias de desarrollo (pytest, httpx)
└── .env.example                    # Plantilla de variables de entorno
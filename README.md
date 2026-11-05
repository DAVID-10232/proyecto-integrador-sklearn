# 🧠 RikiNode AI Service — Proyecto Integrador S17

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3-F7931E?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Prometheus](https://img.shields.io/badge/Monitoring-Prometheus-E6522C?logo=prometheus&logoColor=white)](https://prometheus.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

> **Curso:** Implementación de Sistemas Inteligentes (Semana 17)  
> **Estado:** ✅ Completado — 100/100 en pruebas automatizadas.

## 🎯 Finalidad del Proyecto

El objetivo de este sistema es demostrar la implementación práctica de una solución de Inteligencia Artificial lista para producción. Consiste en una API REST segura que consume un modelo de Machine Learning preentrenado para realizar **análisis de sentimiento** (clasificación POSITIVE/NEGATIVE) en tiempo real. 

El sistema integra los 5 pilares fundamentales solicitados:
1. **Modelo Preentrenado:** Pipeline de `scikit-learn` (TF-IDF + LogisticRegression).
2. **API Segura:** Autenticación JWT y validación de datos con Pydantic.
3. **Contenerización:** Docker y Docker Compose (multi-stage build).
4. **Automatización:** Tareas programadas con APScheduler y CI/CD.
5. **Monitoreo:** Métricas expuestas para Prometheus y Dashboard interactivo.

---

## ⚙️ ¿Cómo funciona?

1. **Entrenamiento:** El script `train_model.py` entrena un modelo usando un dataset de texto y lo serializa en `models/sentiment_model.joblib`.
2. **Autenticación:** El cliente envía sus credenciales a `/api/v1/auth/login` y recibe un Token JWT.
3. **Inferencia:** El cliente envía un texto a `/api/v1/predict/` incluyendo el token en los headers. El modelo vectoriza el texto (TF-IDF) y predice la clase junto a un porcentaje de confianza.
4. **Monitoreo:** Cada predicción incrementa los contadores en `/metrics`. Un dashboard web consume estos datos para graficar la distribución de sentimientos y la latencia en tiempo real.
5. **Automatización:** Un proceso en segundo plano (APScheduler) verifica cada 5 minutos que el modelo esté cargado en memoria, reintentando la carga si falló.

---

## 🚀 Tecnologías Utilizadas

- **Backend:** Python 3.12, FastAPI, Uvicorn.
- **Machine Learning:** scikit-learn, joblib, pandas, numpy.
- **Seguridad:** python-jose (JWT), passlib (bcrypt).
- **DevOps:** Docker, Docker Compose, GitHub Actions.
- **Observabilidad:** Prometheus-client.
- **Frontend (Dashboard):** HTML5, CSS3, JavaScript, Chart.js.

---

## 📂 Estructura del Proyecto

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
│   └── sentiment_model.joblib      # Modelo serializado
│
├── .github/workflows/deploy.yml    # CI/CD (GitHub Actions)
├── .vscode/                        # Configuración de VS Code (launch.json)
├── Dockerfile                      # Imagen de producción (Multi-stage)
├── docker-compose.yml              # Orquestación local
├── requirements.txt                # Dependencias de producción
├── requirements-dev.txt            # Dependencias de desarrollo (pytest, httpx)
└── .env.example                    # Plantilla de variables de entorno

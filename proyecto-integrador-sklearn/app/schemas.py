from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class PredictRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Texto a analizar",
        examples=["I love this product!"],
    )


class PredictResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    label: str = Field(description="POSITIVE o NEGATIVE")
    score: float = Field(description="Confianza de 0 a 1")
    model: str


class BatchPredictRequest(BaseModel):
    texts: List[str] = Field(
        ...,
        min_length=1,
        max_length=32,
        description="Lista de textos (máx 32)",
    )


class BatchPredictResponse(BaseModel):
    results: List[PredictResponse]


class HealthResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    status: str
    version: str
    model_loaded: bool
    model_name: Optional[str] = None

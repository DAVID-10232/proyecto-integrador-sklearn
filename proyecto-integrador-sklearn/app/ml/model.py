"""
Carga y consume un modelo preentrenado (scikit-learn + joblib).

El modelo se entrenó con scripts/train_model.py y se incluye en la imagen.
"""
from typing import List, Dict, Optional
from pathlib import Path
import logging
import joblib

logger = logging.getLogger(__name__)


class SentimentModel:
    """Wrapper sobre un pipeline de scikit-learn (TF-IDF + LogReg)."""

    def __init__(self):
        self.pipeline = None
        self.model_name: Optional[str] = None
        self.is_loaded: bool = False

    def load(self, model_path: str, model_name: str) -> bool:
        """Carga el modelo serializado con joblib."""
        try:
            path = Path(model_path)
            if not path.exists():
                logger.error(f"Model file not found: {path}")
                self.is_loaded = False
                return False

            logger.info(f"Loading model: {path}")
            self.pipeline = joblib.load(path)
            self.model_name = model_name
            self.is_loaded = True
            logger.info("Model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.is_loaded = False
            return False

    def predict(self, text: str) -> Dict:
        """Inferencia de un texto."""
        if not self.is_loaded or self.pipeline is None:
            raise RuntimeError("Model is not loaded")

        label = self.pipeline.predict([text])[0]
        proba = self.pipeline.predict_proba([text])[0]
        score = float(max(proba))

        return {"label": str(label), "score": round(score, 4)}

    def predict_batch(self, texts: List[str]) -> List[Dict]:
        """Inferencia por lote."""
        if not self.is_loaded or self.pipeline is None:
            raise RuntimeError("Model is not loaded")

        labels = self.pipeline.predict(texts)
        probas = self.pipeline.predict_proba(texts)

        return [
            {"label": str(lbl), "score": round(float(max(pr)), 4)}
            for lbl, pr in zip(labels, probas)
        ]

    def info(self) -> Dict:
        return {
            "model_name": self.model_name,
            "task": "sentiment-analysis",
            "framework": "scikit-learn",
            "is_loaded": self.is_loaded,
        }


sentiment_model = SentimentModel()

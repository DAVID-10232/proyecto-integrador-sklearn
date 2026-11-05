"""
Entrena un modelo de análisis de sentimiento con TF-IDF + LogisticRegression.

Uso:
    python scripts/train_model.py

Genera:
    models/sentiment_model.joblib

Este script corre LOCALMENTE una sola vez (o en CI antes del build).
El archivo .joblib se incluye en la imagen Docker.
"""
from pathlib import Path
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold

# Dataset embebido (reemplazable por un CSV real)
DATASET = [
    # POSITIVE
    ("I love this product", "POSITIVE"),
    ("This is amazing", "POSITIVE"),
    ("Excellent quality, very happy", "POSITIVE"),
    ("Best purchase I have made", "POSITIVE"),
    ("Highly recommended", "POSITIVE"),
    ("Fantastic experience, will buy again", "POSITIVE"),
    ("Superb quality and fast shipping", "POSITIVE"),
    ("Very satisfied with this", "POSITIVE"),
    ("Outstanding performance", "POSITIVE"),
    ("Absolutely perfect", "POSITIVE"),
    ("Great value for money", "POSITIVE"),
    ("Works exactly as described", "POSITIVE"),
    ("Delighted with the result", "POSITIVE"),
    ("Top notch customer service", "POSITIVE"),
    ("Could not be happier", "POSITIVE"),
    ("Wonderful, exceeded expectations", "POSITIVE"),
    ("Brilliant product", "POSITIVE"),
    ("Impressed with the quality", "POSITIVE"),
    ("Beautiful design and sturdy", "POSITIVE"),
    ("Five stars, highly recommended", "POSITIVE"),
    ("The product arrived in great condition", "POSITIVE"),
    ("Very useful and practical", "POSITIVE"),
    ("I am very happy with my order", "POSITIVE"),
    ("Fast delivery and well packaged", "POSITIVE"),
    ("Excellent customer support", "POSITIVE"),
    # POSITIVE (ampliado)
    ("I really love it, works great", "POSITIVE"),
    ("Amazing product, totally worth it", "POSITIVE"),
    ("Great quality and great price", "POSITIVE"),
    ("This exceeded my expectations", "POSITIVE"),
    ("Very good, I would buy it again", "POSITIVE"),
    ("Love it, perfect fit", "POSITIVE"),
    ("Awesome, works perfectly", "POSITIVE"),
    ("Really good quality, I recommend it", "POSITIVE"),
    ("Best product ever, thank you", "POSITIVE"),
    ("Super happy with this purchase", "POSITIVE"),
    ("Excellent service and fast response", "POSITIVE"),
    ("The quality is outstanding", "POSITIVE"),
    ("Pleasantly surprised, great product", "POSITIVE"),
    ("Good value, nice and sturdy", "POSITIVE"),
    ("I am delighted, it is fantastic", "POSITIVE"),
    ("Easy to use and very reliable", "POSITIVE"),
    ("Lovely product, arrived early", "POSITIVE"),
    ("Perfect, exactly what I needed", "POSITIVE"),
    ("Wonderful quality, will recommend to friends", "POSITIVE"),
    ("Great experience from start to finish", "POSITIVE"),
    ("This is the best thing I bought this year", "POSITIVE"),
    ("Incredible performance, very fast", "POSITIVE"),
    ("Happy customer, great support team", "POSITIVE"),
    ("Nice product, good packaging, fast delivery", "POSITIVE"),
    ("I am impressed, it works wonderfully", "POSITIVE"),
    ("Truly excellent, five stars", "POSITIVE"),
    ("Good, solid and well made", "POSITIVE"),
    ("Love the design, love the quality", "POSITIVE"),
    ("Very pleased, it is great", "POSITIVE"),
    ("Smooth experience and friendly staff", "POSITIVE"),
    # NEGATIVE
    ("I hate this product", "NEGATIVE"),
    ("This is terrible", "NEGATIVE"),
    ("Terrible quality, very disappointed", "NEGATIVE"),
    ("Worst purchase ever", "NEGATIVE"),
    ("Do not recommend", "NEGATIVE"),
    ("Horrible experience, never again", "NEGATIVE"),
    ("Awful quality and slow shipping", "NEGATIVE"),
    ("Very unsatisfied", "NEGATIVE"),
    ("Poor performance", "NEGATIVE"),
    ("Completely broken on arrival", "NEGATIVE"),
    ("Waste of money", "NEGATIVE"),
    ("Does not work as described", "NEGATIVE"),
    ("Frustrated with the result", "NEGATIVE"),
    ("Rude customer service", "NEGATIVE"),
    ("Extremely disappointed", "NEGATIVE"),
    ("Defective, returning it", "NEGATIVE"),
    ("Useless product", "NEGATIVE"),
    ("Not worth the price", "NEGATIVE"),
    ("Cheap materials and flimsy", "NEGATIVE"),
    ("One star, avoid", "NEGATIVE"),
    ("The product arrived damaged", "NEGATIVE"),
    ("Not useful at all", "NEGATIVE"),
    ("I regret this order", "NEGATIVE"),
    ("Very slow delivery and bad packaging", "NEGATIVE"),
    ("Unhelpful and rude", "NEGATIVE"),
    # NEGATIVE (ampliado)
    ("I really hate it, it does not work", "NEGATIVE"),
    ("Awful product, total waste", "NEGATIVE"),
    ("Bad quality and bad price", "NEGATIVE"),
    ("This did not meet my expectations", "NEGATIVE"),
    ("Very bad, I would not buy it again", "NEGATIVE"),
    ("Hate it, terrible fit", "NEGATIVE"),
    ("Awful, stopped working after a day", "NEGATIVE"),
    ("Really bad quality, I do not recommend it", "NEGATIVE"),
    ("Worst product ever, avoid it", "NEGATIVE"),
    ("Super unhappy with this purchase", "NEGATIVE"),
    ("Terrible service and slow response", "NEGATIVE"),
    ("The quality is horrible", "NEGATIVE"),
    ("Unpleasantly surprised, poor product", "NEGATIVE"),
    ("Bad value, cheap and fragile", "NEGATIVE"),
    ("I am angry, it is garbage", "NEGATIVE"),
    ("Hard to use and very unreliable", "NEGATIVE"),
    ("Ugly product, arrived late", "NEGATIVE"),
    ("Useless, not what I needed", "NEGATIVE"),
    ("Disgusting quality, will not recommend to anyone", "NEGATIVE"),
    ("Bad experience from start to finish", "NEGATIVE"),
    ("This is the worst thing I bought this year", "NEGATIVE"),
    ("Terrible performance, very slow", "NEGATIVE"),
    ("Unhappy customer, terrible support team", "NEGATIVE"),
    ("Bad product, bad packaging, late delivery", "NEGATIVE"),
    ("I am disappointed, it works poorly", "NEGATIVE"),
    ("Truly awful, zero stars", "NEGATIVE"),
    ("Bad, weak and badly made", "NEGATIVE"),
    ("Hate the design, hate the quality", "NEGATIVE"),
    ("Very displeased, it is bad", "NEGATIVE"),
    ("Rough experience and rude staff", "NEGATIVE"),
]


def main():
    print("=" * 60)
    print("ENTRENANDO MODELO DE SENTIMIENTO")
    print("=" * 60)

    texts = [x[0] for x in DATASET]
    labels = [x[1] for x in DATASET]

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )
    print(f"Train: {len(X_train)} | Test: {len(X_test)}")

    # Pipeline: TF-IDF + LogisticRegression
    pipeline = Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    ngram_range=(1, 1),
                    max_features=5000,
                    lowercase=True,
                    stop_words="english",
                ),
            ),
            (
                "clf",
                LogisticRegression(max_iter=1000, C=10.0, random_state=42),
            ),
        ]
    )

    # Entrenar
    print("\nEntrenando...")
    pipeline.fit(X_train, y_train)

    # Evaluar
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nAccuracy en test: {acc:.4f}")
    print("\nReporte:")
    print(classification_report(y_test, y_pred, zero_division=0))

    # Validación cruzada (más confiable que un split pequeño)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(pipeline, texts, labels, cv=cv)
    print(f"Accuracy validación cruzada (5-fold): {cv_scores.mean():.4f}")

    # Reentrenar con TODOS los datos para el modelo final
    pipeline.fit(texts, labels)

    # Guardar (siempre relativo a la raíz del proyecto)
    project_root = Path(__file__).resolve().parent.parent
    output_dir = project_root / "models"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "sentiment_model.joblib"

    joblib.dump(pipeline, output_path)
    print(f"\n✓ Modelo guardado en: {output_path}")
    print(f"✓ Tamaño: {output_path.stat().st_size / 1024:.1f} KB")

    # Smoke test
    test_phrases = [
        "This product is amazing",
        "I really hate it",
        "Best purchase of my life",
        "Terrible, do not buy",
    ]
    print("\nPruebas rápidas:")
    for phrase in test_phrases:
        pred = pipeline.predict([phrase])[0]
        proba = pipeline.predict_proba([phrase])[0]
        score = float(max(proba))
        print(f"  '{phrase}' → {pred} ({score:.2%})")


if __name__ == "__main__":
    main()

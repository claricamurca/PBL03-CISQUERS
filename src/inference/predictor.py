from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
import tensorflow as tf

from src.config import MODEL_FILE, PREPROCESSOR_FILE, SCHEMA_FILE


@dataclass
class PredictionResult:
    risk_probability: float
    predicted_class: int
    risk_label: str
    threshold: float


class StudentRiskPredictor:
    def __init__(
        self,
        model_path: Path = MODEL_FILE,
        preprocessor_path: Path = PREPROCESSOR_FILE,
        schema_path: Path = SCHEMA_FILE,
        threshold: float = 0.5,
    ) -> None:
        self.model_path = model_path
        self.preprocessor_path = preprocessor_path
        self.schema_path = schema_path
        self.threshold = threshold
        self.model = None
        self.preprocessor = None
        self.schema: dict[str, Any] = {}

    def load(self) -> None:
        if not self.model_path.exists() or not self.preprocessor_path.exists():
            raise FileNotFoundError(
                "Model artifacts were not found. Run `python -m src.training.train_mlp` first."
            )

        self.model = tf.keras.models.load_model(self.model_path)
        self.preprocessor = joblib.load(self.preprocessor_path)
        self.schema = json.loads(self.schema_path.read_text(encoding="utf-8"))

    @property
    def feature_columns(self) -> list[str]:
        return self.schema.get("feature_columns", [])

    def predict_one(self, payload: dict[str, Any]) -> PredictionResult:
        if self.model is None or self.preprocessor is None:
            self.load()

        missing_columns = [column for column in self.feature_columns if column not in payload]
        if missing_columns:
            raise ValueError(f"Missing required feature(s): {', '.join(missing_columns)}")

        frame = pd.DataFrame([{column: payload[column] for column in self.feature_columns}])
        transformed = self.preprocessor.transform(frame)
        probability = float(self.model.predict(transformed, verbose=0).reshape(-1)[0])
        predicted_class = int(probability >= self.threshold)
        label = "Risco de baixo desempenho" if predicted_class == 1 else "Sem risco elevado"

        return PredictionResult(
            risk_probability=probability,
            predicted_class=predicted_class,
            risk_label=label,
            threshold=self.threshold,
        )


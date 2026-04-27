from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
import tensorflow as tf

from src.config import MODEL_FILE, PREPROCESSOR_FILE, SCHEMA_FILE

logger = logging.getLogger(__name__)


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

    def is_loaded(self) -> bool:
        return self.model is not None and self.preprocessor is not None and bool(self.schema)

    def load(self) -> None:
        if self.is_loaded():
            return

        missing_paths = [
            str(path)
            for path in (self.model_path, self.preprocessor_path, self.schema_path)
            if not path.exists()
        ]
        if missing_paths:
            raise FileNotFoundError(
                "Model artifacts were not found: " + ", ".join(missing_paths)
            )

        schema = json.loads(self.schema_path.read_text(encoding="utf-8"))
        preprocessor = joblib.load(self.preprocessor_path)
        model = tf.keras.models.load_model(self.model_path, compile=False)

        if not getattr(model, "weights", None):
            raise ValueError(
                f"Loaded Keras model has no weights after deserialization: {self.model_path}"
            )

        self.schema = schema
        self.preprocessor = preprocessor
        self.model = model
        logger.info(
            "Loaded predictor artifacts from %s with %d feature columns.",
            self.model_path,
            len(self.feature_columns),
        )

    @property
    def feature_columns(self) -> list[str]:
        return self.schema.get("feature_columns", [])

    def predict_one(self, payload: dict[str, Any]) -> PredictionResult:
        if not self.is_loaded():
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

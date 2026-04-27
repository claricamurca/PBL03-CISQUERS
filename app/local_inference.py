from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.inference.predictor import PredictionResult, StudentRiskPredictor


@lru_cache(maxsize=1)
def get_local_predictor() -> StudentRiskPredictor:
    predictor = StudentRiskPredictor()
    predictor.load()
    return predictor


def predict_student_risk(payload: dict[str, Any]) -> PredictionResult:
    predictor = get_local_predictor()
    return predictor.predict_one(payload)

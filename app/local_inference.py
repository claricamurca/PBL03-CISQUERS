from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.inference.predictor import PredictionResult, StudentRiskPredictor


@st.cache_resource(show_spinner=False)
def get_local_predictor() -> StudentRiskPredictor:
    predictor = StudentRiskPredictor()
    predictor.load()
    return predictor


def predict_student_risk(payload: dict[str, Any]) -> PredictionResult:
    predictor = get_local_predictor()
    return predictor.predict_one(payload)

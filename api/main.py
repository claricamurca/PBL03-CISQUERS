from __future__ import annotations

from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.inference.predictor import StudentRiskPredictor


class StudentFeatures(BaseModel):
    school: Literal["GP", "MS"] = "GP"
    sex: Literal["F", "M"] = "F"
    age: int = Field(16, ge=15, le=22)
    address: Literal["U", "R"] = "U"
    famsize: Literal["LE3", "GT3"] = "GT3"
    Pstatus: Literal["T", "A"] = "T"
    Medu: int = Field(2, ge=0, le=4)
    Fedu: int = Field(2, ge=0, le=4)
    Mjob: Literal["teacher", "health", "services", "at_home", "other"] = "other"
    Fjob: Literal["teacher", "health", "services", "at_home", "other"] = "other"
    reason: Literal["home", "reputation", "course", "other"] = "course"
    guardian: Literal["mother", "father", "other"] = "mother"
    traveltime: int = Field(1, ge=1, le=4)
    studytime: int = Field(2, ge=1, le=4)
    failures: int = Field(0, ge=0, le=4)
    schoolsup: Literal["yes", "no"] = "no"
    famsup: Literal["yes", "no"] = "yes"
    paid: Literal["yes", "no"] = "no"
    activities: Literal["yes", "no"] = "yes"
    nursery: Literal["yes", "no"] = "yes"
    higher: Literal["yes", "no"] = "yes"
    internet: Literal["yes", "no"] = "yes"
    romantic: Literal["yes", "no"] = "no"
    famrel: int = Field(4, ge=1, le=5)
    freetime: int = Field(3, ge=1, le=5)
    goout: int = Field(3, ge=1, le=5)
    Dalc: int = Field(1, ge=1, le=5)
    Walc: int = Field(2, ge=1, le=5)
    health: int = Field(3, ge=1, le=5)
    absences: int = Field(4, ge=0, le=100)
    G1: int = Field(10, ge=0, le=20)
    G2: int = Field(10, ge=0, le=20)
    subject: Literal["mathematics", "portuguese"] = "mathematics"

    model_config = {
        "json_schema_extra": {
            "example": {
                "school": "GP",
                "sex": "F",
                "age": 16,
                "address": "U",
                "famsize": "GT3",
                "Pstatus": "T",
                "Medu": 3,
                "Fedu": 2,
                "Mjob": "services",
                "Fjob": "other",
                "reason": "course",
                "guardian": "mother",
                "traveltime": 1,
                "studytime": 2,
                "failures": 0,
                "schoolsup": "no",
                "famsup": "yes",
                "paid": "no",
                "activities": "yes",
                "nursery": "yes",
                "higher": "yes",
                "internet": "yes",
                "romantic": "no",
                "famrel": 4,
                "freetime": 3,
                "goout": 3,
                "Dalc": 1,
                "Walc": 2,
                "health": 3,
                "absences": 4,
                "G1": 9,
                "G2": 8,
                "subject": "mathematics",
            }
        }
    }


class PredictionResponse(BaseModel):
    risk_probability: float
    predicted_class: int
    risk_label: str
    threshold: float


app = FastAPI(
    title="Sistema Inteligente de Previsao de Desempenho Escolar",
    description="API para prever risco de baixo desempenho escolar com MLP.",
    version="1.0.0",
)
predictor = StudentRiskPredictor()


@app.on_event("startup")
def load_artifacts() -> None:
    predictor.load()


@app.get("/")
def root() -> dict[str, str]:
    return {
        "project": "Sistema Inteligente de Previsao de Desempenho Escolar",
        "status": "online",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/features")
def features() -> dict:
    return predictor.schema


@app.post("/predict", response_model=PredictionResponse)
def predict(features: StudentFeatures) -> PredictionResponse:
    try:
        result = predictor.predict_one(features.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return PredictionResponse(**result.__dict__)


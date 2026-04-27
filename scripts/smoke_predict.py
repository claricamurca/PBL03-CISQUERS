import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.inference.predictor import StudentRiskPredictor


SAMPLE_STUDENT = {
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


if __name__ == "__main__":
    result = StudentRiskPredictor().predict_one(SAMPLE_STUDENT)
    print(
        {
            "risk_probability": round(result.risk_probability, 4),
            "predicted_class": result.predicted_class,
            "risk_label": result.risk_label,
        }
    )


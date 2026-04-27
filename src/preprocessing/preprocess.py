from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.config import (
    FINAL_GRADE_COLUMN,
    LOW_PERFORMANCE_THRESHOLD,
    PREPROCESSOR_FILE,
    PROCESSED_DATA_FILE,
    SCHEMA_FILE,
    TARGET_COLUMN,
    ensure_project_dirs,
)


FEATURE_DESCRIPTIONS = {
    "school": "Student school: GP or MS",
    "sex": "Student sex: F or M",
    "age": "Student age",
    "address": "Home address type: U urban or R rural",
    "famsize": "Family size: LE3 or GT3",
    "Pstatus": "Parents' cohabitation status: T together or A apart",
    "Medu": "Mother education level from 0 to 4",
    "Fedu": "Father education level from 0 to 4",
    "Mjob": "Mother job category",
    "Fjob": "Father job category",
    "reason": "Reason for choosing school",
    "guardian": "Student guardian",
    "traveltime": "Home to school travel time from 1 to 4",
    "studytime": "Weekly study time from 1 to 4",
    "failures": "Number of past class failures",
    "schoolsup": "Extra educational school support",
    "famsup": "Family educational support",
    "paid": "Extra paid classes",
    "activities": "Extra-curricular activities",
    "nursery": "Attended nursery school",
    "higher": "Wants higher education",
    "internet": "Internet access at home",
    "romantic": "In a romantic relationship",
    "famrel": "Quality of family relationships from 1 to 5",
    "freetime": "Free time after school from 1 to 5",
    "goout": "Going out with friends from 1 to 5",
    "Dalc": "Workday alcohol consumption from 1 to 5",
    "Walc": "Weekend alcohol consumption from 1 to 5",
    "health": "Current health status from 1 to 5",
    "absences": "Number of school absences",
    "G1": "First period grade from 0 to 20",
    "G2": "Second period grade from 0 to 20",
    "subject": "Course file source: mathematics or portuguese",
}


@dataclass(frozen=True)
class PreparedData:
    x: pd.DataFrame
    y: pd.Series
    feature_columns: list[str]
    numeric_features: list[str]
    categorical_features: list[str]


def create_target(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Create the binary target where 1 means risk of final grade below 10."""
    if FINAL_GRADE_COLUMN not in dataframe.columns:
        raise KeyError(f"Expected final grade column `{FINAL_GRADE_COLUMN}` in dataset.")

    prepared = dataframe.copy()
    prepared[TARGET_COLUMN] = (
        prepared[FINAL_GRADE_COLUMN] < LOW_PERFORMANCE_THRESHOLD
    ).astype(int)
    return prepared


def clean_dataset(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Basic cleaning for the UCI CSVs, keeping transformations reproducible."""
    cleaned = dataframe.copy()
    cleaned.columns = [column.strip() for column in cleaned.columns]
    cleaned = cleaned.drop_duplicates().reset_index(drop=True)

    for column in cleaned.select_dtypes(include="object").columns:
        cleaned[column] = cleaned[column].astype(str).str.strip()

    return cleaned


def prepare_features(dataframe: pd.DataFrame) -> PreparedData:
    prepared = create_target(clean_dataset(dataframe))
    x = prepared.drop(columns=[TARGET_COLUMN, FINAL_GRADE_COLUMN])
    y = prepared[TARGET_COLUMN]

    categorical_features = x.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    numeric_features = [column for column in x.columns if column not in categorical_features]

    return PreparedData(
        x=x,
        y=y,
        feature_columns=x.columns.tolist(),
        numeric_features=numeric_features,
        categorical_features=categorical_features,
    )


def build_preprocessor(
    numeric_features: list[str],
    categorical_features: list[str],
) -> ColumnTransformer:
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric_features),
            ("categorical", categorical_pipeline, categorical_features),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def save_processed_dataset(dataframe: pd.DataFrame) -> None:
    ensure_project_dirs()
    create_target(clean_dataset(dataframe)).to_csv(PROCESSED_DATA_FILE, index=False)


def save_preprocessing_artifacts(
    preprocessor: ColumnTransformer,
    prepared_data: PreparedData,
    extra_schema: dict[str, Any] | None = None,
) -> None:
    ensure_project_dirs()
    joblib.dump(preprocessor, PREPROCESSOR_FILE)

    schema = {
        "target": TARGET_COLUMN,
        "target_definition": f"1 when G3 < {LOW_PERFORMANCE_THRESHOLD}, otherwise 0",
        "excluded_columns": [FINAL_GRADE_COLUMN, TARGET_COLUMN],
        "feature_columns": prepared_data.feature_columns,
        "numeric_features": prepared_data.numeric_features,
        "categorical_features": prepared_data.categorical_features,
        "feature_descriptions": {
            column: FEATURE_DESCRIPTIONS.get(column, "")
            for column in prepared_data.feature_columns
        },
    }

    if extra_schema:
        schema.update(extra_schema)

    SCHEMA_FILE.write_text(json.dumps(schema, indent=2), encoding="utf-8")


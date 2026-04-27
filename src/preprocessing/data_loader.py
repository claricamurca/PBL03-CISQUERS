from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

from src.config import MATH_FILE, PORTUGUESE_FILE, RAW_DATA_DIR, ensure_project_dirs


UCI_STUDENT_PERFORMANCE_URL = (
    "https://archive.ics.uci.edu/static/public/320/student+performance.zip"
)


def download_uci_student_performance(destination_dir: Path = RAW_DATA_DIR) -> None:
    """Download the official UCI Student Performance files into data/raw."""
    ensure_project_dirs()
    zip_path = destination_dir / "student_performance.zip"

    response = requests.get(UCI_STUDENT_PERFORMANCE_URL, timeout=60)
    response.raise_for_status()
    zip_path.write_bytes(response.content)

    with zipfile.ZipFile(zip_path) as archive:
        names = archive.namelist()
        if "student-mat.csv" in names and "student-por.csv" in names:
            source_archive = archive
        else:
            nested_zip_name = next(name for name in names if name.endswith("student.zip"))
            nested_zip = io.BytesIO(archive.read(nested_zip_name))
            source_archive = zipfile.ZipFile(nested_zip)

        for member in ["student-mat.csv", "student-por.csv"]:
            target = destination_dir / member
            target.write_bytes(source_archive.read(member))


def _read_student_file(path: Path, subject: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset file not found: {path}. Run `python scripts/download_dataset.py` "
            "or place the UCI CSV files in data/raw."
        )

    dataframe = pd.read_csv(path, sep=";")
    dataframe["subject"] = subject
    return dataframe


def load_student_performance_data(
    include_math: bool = True,
    include_portuguese: bool = True,
) -> pd.DataFrame:
    """Load the Student Performance CSVs and add a subject indicator."""
    frames: list[pd.DataFrame] = []

    if include_math:
        frames.append(_read_student_file(MATH_FILE, "mathematics"))

    if include_portuguese:
        frames.append(_read_student_file(PORTUGUESE_FILE, "portuguese"))

    if not frames:
        raise ValueError("At least one subject file must be selected.")

    return pd.concat(frames, ignore_index=True)

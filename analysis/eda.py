from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

from src.config import FINAL_GRADE_COLUMN, LOW_PERFORMANCE_THRESHOLD, OUTPUTS_DIR, ensure_project_dirs
from src.preprocessing.data_loader import load_student_performance_data
from src.preprocessing.preprocess import create_target


def run_eda() -> None:
    ensure_project_dirs()
    data = create_target(load_student_performance_data())

    summary = {
        "rows": len(data),
        "columns": len(data.columns),
        "low_performance_rate": float(data["risk_low_performance"].mean()),
        "missing_values": data.isna().sum().to_dict(),
        "final_grade_summary": data[FINAL_GRADE_COLUMN].describe().to_dict(),
    }
    pd.Series(summary, dtype="object").to_json(
        OUTPUTS_DIR / "eda_summary.json",
        indent=2,
        force_ascii=False,
    )

    plt.figure(figsize=(8, 5))
    data[FINAL_GRADE_COLUMN].hist(bins=20, color="#2f6f73", edgecolor="white")
    plt.axvline(
        LOW_PERFORMANCE_THRESHOLD,
        color="#c43c35",
        linestyle="--",
        label=f"Risk threshold: G3 < {LOW_PERFORMANCE_THRESHOLD}",
    )
    plt.title("Distribution of Final Grades (G3)")
    plt.xlabel("Final grade")
    plt.ylabel("Number of students")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUTS_DIR / "final_grade_distribution.png", dpi=160)
    plt.close()

    risk_by_failures = (
        data.groupby("failures")["risk_low_performance"]
        .mean()
        .reset_index()
        .rename(columns={"risk_low_performance": "risk_rate"})
    )
    plt.figure(figsize=(8, 5))
    plt.bar(risk_by_failures["failures"].astype(str), risk_by_failures["risk_rate"], color="#7b6fbd")
    plt.title("Low Performance Risk by Previous Failures")
    plt.xlabel("Previous failures")
    plt.ylabel("Risk rate")
    plt.tight_layout()
    plt.savefig(OUTPUTS_DIR / "risk_by_previous_failures.png", dpi=160)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.scatter(
        data["G2"],
        data[FINAL_GRADE_COLUMN],
        c=data["risk_low_performance"],
        cmap="coolwarm",
        alpha=0.7,
    )
    plt.title("Second Period Grade vs Final Grade")
    plt.xlabel("G2")
    plt.ylabel("G3")
    plt.tight_layout()
    plt.savefig(OUTPUTS_DIR / "g2_vs_final_grade.png", dpi=160)
    plt.close()


if __name__ == "__main__":
    run_eda()
    print("EDA outputs saved in outputs/.")


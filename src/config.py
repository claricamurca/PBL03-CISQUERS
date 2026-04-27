from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

MATH_FILE = RAW_DATA_DIR / "student-mat.csv"
PORTUGUESE_FILE = RAW_DATA_DIR / "student-por.csv"
PROCESSED_DATA_FILE = PROCESSED_DATA_DIR / "student_performance_processed.csv"

MODEL_FILE = MODELS_DIR / "mlp_student_risk.h5"
PREPROCESSOR_FILE = MODELS_DIR / "preprocessor.joblib"
SCHEMA_FILE = MODELS_DIR / "feature_schema.json"
METRICS_FILE = OUTPUTS_DIR / "metrics.json"
TRAINING_HISTORY_FILE = OUTPUTS_DIR / "training_history.csv"

TARGET_COLUMN = "risk_low_performance"
FINAL_GRADE_COLUMN = "G3"
LOW_PERFORMANCE_THRESHOLD = 10

RANDOM_STATE = 42
TEST_SIZE = 0.2
VALIDATION_SIZE = 0.2


def ensure_project_dirs() -> None:
    for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR, OUTPUTS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

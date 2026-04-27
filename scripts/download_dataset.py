import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.preprocessing.data_loader import download_uci_student_performance


if __name__ == "__main__":
    download_uci_student_performance()
    print("UCI Student Performance dataset downloaded to data/raw.")

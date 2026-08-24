from pathlib import Path
import pandas as pd


def load_cost_data(file_path):
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Cost data file not found: {path}")

    df = pd.read_csv(path)

    return df
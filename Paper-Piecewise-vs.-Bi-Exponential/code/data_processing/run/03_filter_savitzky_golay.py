"""Step 3a of the treadmill pipeline: Savitzky-Golay smoothing (one of two
competing smoothing methods this project compares).

Reads `treadmill_data/prepared_data/preparedTimeTrial.csv` and applies a
Savitzky-Golay filter (local polynomial smoothing) independently to each
participant's VO2 column, writing
`treadmill_data/prepared_data/sg_filtered_4mintt.csv`.

The alternative smoothing method (Butterworth low-pass) lives in
`04_filter_butterworth.py`; both, plus the unfiltered data, are fed into
the two modeling scripts (`05_fit_piecewise.py`, `06_fit_biexponential.py`)
as the "sg" / "bw" / "cleaned" comparison arms.

Run from anywhere, e.g. `python code/data_processing/run/03_filter_savitzky_golay.py`
from the repo root.
"""

from pathlib import Path

import pandas as pd
from scipy.signal import savgol_filter

REPO_ROOT = Path(__file__).resolve().parents[3]
INPUT_PATH = REPO_ROOT / "treadmill_data" / "prepared_data" / "preparedTimeTrial.csv"
OUTPUT_PATH = REPO_ROOT / "treadmill_data" / "prepared_data" / "sg_filtered_4mintt.csv"

WINDOW_LENGTH = 7  # samples; must be odd and <= number of data points
POLY_ORDER = 3


def filter_with_savitzky_golay(df, window_length=WINDOW_LENGTH, polyorder=POLY_ORDER):
    filtered = df.copy()
    for col in df.columns:
        if col == "time":
            continue
        if len(df[col]) >= window_length:
            filtered[col] = savgol_filter(df[col], window_length, polyorder)
        # else: too few points for this window; leave the column unchanged.
    return filtered


if __name__ == "__main__":
    df = pd.read_csv(INPUT_PATH)
    filtered_df = filter_with_savitzky_golay(df)
    filtered_df.to_csv(OUTPUT_PATH, index=False)
    print(f"SG-smoothed data saved to {OUTPUT_PATH}")

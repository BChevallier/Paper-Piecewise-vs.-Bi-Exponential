"""Step 3a of the treadmill pipeline: Savitzky-Golay smoothing (one of two
competing smoothing methods this project compares).

Reads `treadmill/data/prepared/time_trial.csv` and applies a
Savitzky-Golay filter (local polynomial smoothing, window 7 samples, poly
order 3 — see `shared/smoothing.py`) independently to each participant's VO2
column, writing `treadmill/data/prepared/time_trial_sg_filtered.csv`.

The alternative smoothing method (Butterworth low-pass) lives in
`04_filter_butterworth.py`; both, plus the unfiltered data, are fed into
the two modeling scripts (`05_fit_piecewise.py`, `06_fit_biexponential.py`)
as the "sg" / "bw" / "cleaned" comparison arms.

Run from anywhere, e.g. `python treadmill/scripts/03_filter_savitzky_golay.py`
from the repo root.
"""

import pandas as pd

from treadmill_common import TIME_TRIAL as INPUT_PATH
from treadmill_common import TIME_TRIAL_SG as OUTPUT_PATH
from smoothing import filter_with_savitzky_golay  # needs treadmill_common imported first (sys.path)


if __name__ == "__main__":
    df = pd.read_csv(INPUT_PATH)
    filtered_df = filter_with_savitzky_golay(df)
    filtered_df.to_csv(OUTPUT_PATH, index=False)
    print(f"SG-smoothed data saved to {OUTPUT_PATH}")

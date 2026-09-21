"""Step 3b of the treadmill pipeline: Butterworth low-pass smoothing (the
other of the two competing smoothing methods this project compares).

Reads `treadmill/data/prepared/time_trial.csv` and applies a
3rd-order Butterworth low-pass filter (zero-phase, via `filtfilt`, cutoff
0.04 Hz — see `shared/smoothing.py`) independently to each participant's VO2
column, writing `treadmill/data/prepared/time_trial_bw_filtered.csv`.

The filter assumes the fixed 5-second sample spacing of the prepared time
trial data (sampling rate 0.2 Hz); it is not derived from the data, so this
script would need updating if the sampling rate ever changes upstream.

The alternative smoothing method (Savitzky-Golay) lives in
`03_filter_savitzky_golay.py`; both, plus the unfiltered data, are fed into
the two modeling scripts (`05_fit_piecewise.py`, `06_fit_biexponential.py`)
as the "sg" / "bw" / "cleaned" comparison arms.

Run from anywhere, e.g. `python treadmill/scripts/04_filter_butterworth.py`
from the repo root.
"""

import pandas as pd

from treadmill_common import TIME_TRIAL as INPUT_PATH
from treadmill_common import TIME_TRIAL_BW as OUTPUT_PATH
from smoothing import filter_with_butterworth  # needs treadmill_common imported first (sys.path)


if __name__ == "__main__":
    df = pd.read_csv(INPUT_PATH)
    filtered_df = filter_with_butterworth(df)
    filtered_df.to_csv(OUTPUT_PATH, index=False)
    print(f"Butterworth-smoothed data saved to {OUTPUT_PATH}")

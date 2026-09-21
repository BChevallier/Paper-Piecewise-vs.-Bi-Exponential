"""Step 3a of the bike pipeline: Savitzky-Golay smoothing.

Same filter and settings as the treadmill's `03_filter_savitzky_golay.py`
(both use `code/data_processing/run/smoothing.py`), applied to each trial's
5-second table from `02_prepare_time_trial_data.py`. Writes
`bike_data/prepared_data/<trial>_sg_filtered.csv`.

Usage:
    python bike_code/03_filter_savitzky_golay.py        # both trials
    python bike_code/03_filter_savitzky_golay.py tt1    # one trial
"""

import sys

import pandas as pd

from bike_common import REPO_ROOT, prepared_path, requested_trials, sg_filtered_path
from smoothing import filter_with_savitzky_golay


if __name__ == "__main__":
    for trial in requested_trials(sys.argv):
        df = pd.read_csv(prepared_path(trial))
        output_path = sg_filtered_path(trial)
        filter_with_savitzky_golay(df).to_csv(output_path, index=False)
        print(f"{trial}: SG-smoothed data saved to {output_path.relative_to(REPO_ROOT)}")

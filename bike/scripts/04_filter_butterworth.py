"""Step 3b of the bike pipeline: Butterworth low-pass smoothing.

Same filter and settings as the treadmill's `04_filter_butterworth.py`
(both use `shared/smoothing.py`), applied to each trial's
5-second table from `02_prepare_time_trial_data.py`. The filter assumes that
5-second spacing, which step 2 guarantees. Writes
`bike/data/prepared/<trial>_time_trial_bw_filtered.csv`.

Usage:
    python bike/scripts/04_filter_butterworth.py        # both trials
    python bike/scripts/04_filter_butterworth.py tt1    # one trial
"""

import sys

import pandas as pd

from bike_common import REPO_ROOT, bw_filtered_path, prepared_path, requested_trials
from smoothing import filter_with_butterworth


if __name__ == "__main__":
    for trial in requested_trials(sys.argv):
        df = pd.read_csv(prepared_path(trial))
        output_path = bw_filtered_path(trial)
        filter_with_butterworth(df).to_csv(output_path, index=False)
        print(f"{trial}: Butterworth-smoothed data saved to {output_path.relative_to(REPO_ROOT)}")

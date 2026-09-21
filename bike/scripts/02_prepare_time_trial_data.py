"""Step 2 of the bike pipeline: build the 5-second V'O2 table for each trial.

The bike counterpart of the treadmill's `02_prepare_time_trial_data.py`.
Reads every participant's per-second CPET CSV (from `01_xml_to_csv.py`),
puts it on trial time with the spiro clock correction (see `bike_common.py`),
and averages V'O2 into 5-second bins from 0 to 240 s. Writes one wide table
per trial — `time` plus one column per participant — to
`bike/data/prepared/<trial>_time_trial.csv`.

Why 5-second bins: the treadmill data comes as 5-second samples, and the
smoothing settings (Savitzky-Golay window of 7 samples, Butterworth cutoff
0.04 Hz at 0.2 Hz sampling) are defined on that grid. Binning the bike data
to the same grid means both modalities are smoothed and fitted identically,
so any difference between them comes from the data, not the pipeline.

Each bin is labelled by its end: the value at time T is the mean over
(T - 5, T]. The t = 0 bin therefore holds the last 5 s before the start —
the pre-trial baseline, matching the treadmill table's t = 0 row.

A participant is skipped, with a message, if any bin is empty.

Usage:
    python bike/scripts/02_prepare_time_trial_data.py        # both trials
    python bike/scripts/02_prepare_time_trial_data.py tt1    # one trial
"""

import sys

import numpy as np
import pandas as pd

from bike_common import (
    FIRST_PARTICIPANT,
    LAST_PARTICIPANT,
    REPO_ROOT,
    TRIAL_DURATION_S,
    converted_path,
    load_delays,
    participant_id,
    prepared_path,
    requested_trials,
    seconds_since_trial_start,
)

BIN_S = 5
BIN_ENDS = np.arange(0, TRIAL_DURATION_S + BIN_S, BIN_S)
VO2_COLUMN = "V'O2"


def binned_vo2(raw_path, delay_s):
    """Mean V'O2 per 5-s bin, indexed by bin end (s since trial start)."""
    df = pd.read_csv(raw_path)
    t = seconds_since_trial_start(pd.to_timedelta(df["t"]), delay_s)
    vo2 = pd.to_numeric(df[VO2_COLUMN], errors="coerce")

    in_window = (t > BIN_ENDS[0] - BIN_S) & (t <= BIN_ENDS[-1])
    bin_end = np.ceil(t[in_window] / BIN_S) * BIN_S
    return vo2[in_window].groupby(bin_end).mean().reindex(BIN_ENDS)


def run(trial):
    delays = load_delays(trial)
    table = pd.DataFrame({"time": BIN_ENDS})

    for participant in range(FIRST_PARTICIPANT, LAST_PARTICIPANT + 1):
        pid = participant_id(participant)
        raw_path = converted_path(trial, pid)
        if not raw_path.exists():
            continue

        delay_s = delays.get(participant)
        if pd.isna(delay_s):
            print(f"{trial} {pid}: no delay recorded, skipped")
            continue

        vo2 = binned_vo2(raw_path, delay_s)
        missing = vo2.index[vo2.isna()]
        if len(missing):
            print(f"{trial} {pid}: no data in bins ending {list(missing)} s, skipped")
            continue

        table[pid] = vo2.to_numpy()

    output_path = prepared_path(trial)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(output_path, index=False)
    n_participants = table.shape[1] - 1
    print(
        f"{trial}: {n_participants} participants x {len(table)} bins "
        f"-> {output_path.relative_to(REPO_ROOT)}"
    )


if __name__ == "__main__":
    for trial in requested_trials(sys.argv):
        run(trial)
